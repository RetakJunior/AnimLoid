"""Asynchronous workers and background threads for AnimLoid GUI."""

import threading
import time
from collections import OrderedDict
from urllib.parse import urlsplit, urlunsplit
from PyQt5.QtCore import QRunnable, QThreadPool
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QSize, Qt
from PyQt5.QtGui import QImage

from weeb_cli.services.details import serialize_details
from weeb_cli.services.scraper import Scraper
from weeb_cli.services.recommendations import get_recommendations
from weeb_cli.services.player import player
from weeb_cli.services.dependency_manager import dependency_manager
from weeb_cli.services.downloader import queue_manager

# QPixmap is a GUI-only resource in Qt.  Keep decoded images as QImage here,
# because QImage may safely be created and resized in a worker thread.  The
# view turns it into a QPixmap only after the signal reaches the GUI thread.
_IMAGE_CACHE = OrderedDict()
_IMAGE_CACHE_LOCK = threading.Lock()
_IMAGE_CACHE_LIMIT = 256
_IMAGE_POOL = QThreadPool()
_IMAGE_POOL.setMaxThreadCount(5)
_ACTIVE_IMAGE_WORKERS = set()
_LIVE_WORKERS = set()


class _ImageSignals(QObject):
    image_loaded = pyqtSignal(str, QImage)
    image_failed = pyqtSignal(str)
    finished = pyqtSignal(object)


class _ImageWorkerReaper(QObject):
    def release(self, worker):
        with _IMAGE_CACHE_LOCK:
            _ACTIVE_IMAGE_WORKERS.discard(worker)


_IMAGE_WORKER_REAPER = _ImageWorkerReaper()


def start_image_worker(worker):
    """Run image requests in a small shared pool, not one thread per card."""
    with _IMAGE_CACHE_LOCK:
        _ACTIVE_IMAGE_WORKERS.add(worker)
    worker.signals.finished.connect(_IMAGE_WORKER_REAPER.release, Qt.QueuedConnection)
    _IMAGE_POOL.start(worker)
    return worker


def start_background_worker(owner, worker):
    """Start a QThread without letting a view destroy it while it is running.

    A user can start another search or leave a detail page while a provider is
    still waiting for a network timeout.  Keeping a reference until `finished`
    prevents Qt's fatal "QThread: Destroyed while thread is still running"
    shutdown path.  It also lets old requests finish harmlessly instead of
    force-stopping them with QThread.terminate().
    """
    active_workers = getattr(owner, "_active_workers", None)
    if active_workers is None:
        active_workers = set()
        owner._active_workers = active_workers

    # A view can be closed or replaced before a slow provider request returns.
    # QThread must outlive its native thread in that case, so do not let Qt
    # destroy it as a child of the view.
    worker.setParent(None)
    active_workers.add(worker)
    _LIVE_WORKERS.add(worker)

    def clean_up():
        active_workers.discard(worker)
        _LIVE_WORKERS.discard(worker)
        worker.deleteLater()

    # QThread subclasses emit from run().  Force this housekeeping callback
    # onto the GUI queue as well; relying on AutoConnection differs between
    # Qt/PyQt builds and can otherwise execute Python cleanup in the worker.
    worker.finished.connect(clean_up, Qt.QueuedConnection)
    worker.start()
    return worker


class ImageLoaderWorker(QRunnable):
    """Download, retry, and decode poster images outside the GUI thread."""

    def __init__(self, url: str, target_size=None, parent=None):
        super().__init__()
        self.url = url
        self.target_size = target_size
        self.signals = _ImageSignals()
        self.setAutoDelete(True)

    def run(self):
        try:
            self._load()
        finally:
            self.signals.finished.emit(self)

    def _load(self):
        width = self.target_size.width() if self.target_size else 0
        height = self.target_size.height() if self.target_size else 0
        url = self._normalise_url(self.url)
        cache_key = (url, width, height)
        try:
            if not url:
                self.signals.image_failed.emit(self.url)
                return

            with _IMAGE_CACHE_LOCK:
                cached_image = _IMAGE_CACHE.get(cache_key)
                if cached_image is not None:
                    _IMAGE_CACHE.move_to_end(cache_key)
            if cached_image is not None:
                self.signals.image_loaded.emit(self.url, cached_image)
                return

            response = self._download(url)
            if response is None or response.status_code != 200 or len(response.content) > 15 * 1024 * 1024:
                self.signals.image_failed.emit(self.url)
                return

            image = QImage()
            if not response.content or not image.loadFromData(response.content):
                self.signals.image_failed.emit(self.url)
                return
            if width > 0 and height > 0:
                image = image.scaled(QSize(width, height), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                left = max(0, (image.width() - width) // 2)
                top = max(0, (image.height() - height) // 2)
                image = image.copy(left, top, width, height)
            with _IMAGE_CACHE_LOCK:
                _IMAGE_CACHE[cache_key] = image
                _IMAGE_CACHE.move_to_end(cache_key)
                while len(_IMAGE_CACHE) > _IMAGE_CACHE_LIMIT:
                    _IMAGE_CACHE.popitem(last=False)
            self.signals.image_loaded.emit(self.url, image)
        except Exception:
            self.signals.image_failed.emit(self.url)

    @staticmethod
    def _normalise_url(url):
        url = (url or "").strip()
        if url.startswith("//"):
            return "https:" + url
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            return ""
        return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))

    @staticmethod
    def _download(url):
        parts = urlsplit(url)
        headers = {
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": f"{parts.scheme}://{parts.netloc}/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        }
        try:
            from curl_cffi import requests as image_requests
            request_options = {"impersonate": "chrome120"}
        except ImportError:
            import requests as image_requests
            request_options = {}

        for attempt in range(2):
            try:
                response = image_requests.get(url, headers=headers, timeout=10, **request_options)
                if response.status_code == 200 or response.status_code < 500:
                    return response
            except Exception:
                if attempt == 1:
                    return None
            if attempt == 0:
                time.sleep(0.25)
        return None




class SearchWorker(QThread):
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, query: str, source_name: str = None):
        super().__init__()
        self.query = query
        self.source_name = source_name

    def run(self):
        try:
            # Each request owns its scraper instance.  Changing global config
            # from a QThread can race with a detail/stream request and make
            # its result come from a different source.
            from weeb_cli.services.scraper import Scraper
            searcher = Scraper(self.source_name)
            results = searcher.search(self.query)
            
            # Standardize results into dicts
            formatted_results = []
            if results:
                for r in results:
                    if hasattr(r, '__dict__'):
                        formatted_results.append({
                            "id": r.id,
                            "slug": r.id,
                            "title": getattr(r, "title", "Anime"),
                            "name": getattr(r, "title", "Anime"),
                            "type": getattr(r, "type", "series"),
                            "cover": getattr(r, "cover", None),
                            "year": getattr(r, "year", None),
                            "playable": getattr(r, "playable", None),
                            "source": self.source_name or "",
                        })
                    elif isinstance(r, dict):
                        result = dict(r)
                        result.setdefault("source", self.source_name or "")
                        formatted_results.append(result)
            
            if not formatted_results and searcher.last_error:
                self.error_occurred.emit(searcher.last_error)
                return
            self.results_ready.emit(formatted_results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class RecommendationsWorker(QThread):
    recommendations_ready = pyqtSignal(list)

    def __init__(self, sort="TRENDING_DESC", force_refresh=False):
        super().__init__()
        self.sort = sort
        self.force_refresh = force_refresh

    def run(self):
        self.recommendations_ready.emit(get_recommendations(self.sort, 12, self.force_refresh))


class DetailsWorker(QThread):
    details_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, slug: str, source_name: str = None):
        super().__init__()
        self.slug = slug
        self.source_name = source_name

    def run(self):
        try:
            client = Scraper(self.source_name)
            details = serialize_details(client.get_details(self.slug))
            if details:
                details["provider"] = self.source_name or ""
                self.details_ready.emit(details)
            else:
                self.error_occurred.emit(client.last_error or "Anime detayları alınamadı. Bağlantıyı kontrol edip yeniden deneyin.")
        except Exception as e:
            self.error_occurred.emit(str(e))


class StreamsWorker(QThread):
    streams_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, anime_id: str, episode_id: str, source_name: str = None):
        super().__init__()
        self.anime_id = anime_id
        self.episode_id = episode_id
        self.source_name = source_name

    def run(self):
        try:
            client = Scraper(self.source_name)
            streams = client.get_streams(self.anime_id, self.episode_id)
            if streams:
                links = [
                    {
                        "url": stream.url,
                        "quality": stream.quality,
                        "server": stream.server,
                        "headers": dict(stream.headers or {}),
                        "subtitles": stream.subtitles,
                    }
                    for stream in streams
                ]
                self.streams_ready.emit(links)
            else:
                self.error_occurred.emit(client.last_error or "Yayın bağlantısı bulunamadı. Başka bir kaynak deneyin.")
        except Exception as e:
            self.error_occurred.emit(str(e))


class PlayWorker(QThread):
    play_finished = pyqtSignal(bool)

    def __init__(self, url: str, title: str = None, headers: dict = None, anime_title: str = None, episode_number: int = None, total_episodes: int = None):
        super().__init__()
        self.url = url
        self.title = title
        self.headers = headers
        self.anime_title = anime_title
        self.episode_number = episode_number
        self.total_episodes = total_episodes

    def run(self):
        try:
            res = player.play(
                url=self.url,
                title=self.title,
                headers=self.headers,
                anime_title=self.anime_title,
                episode_number=self.episode_number,
                total_episodes=self.total_episodes
            )
            self.play_finished.emit(res)
        except Exception:
            self.play_finished.emit(False)


class DependencyCheckWorker(QThread):
    status_ready = pyqtSignal(dict)

    def run(self):
        deps = ["mpv", "ffmpeg", "yt-dlp", "aria2"]
        results = {}
        for dep in deps:
            path = dependency_manager.check_dependency(dep)
            results[dep] = {
                "installed": path is not None,
                "path": path or ""
            }
        self.status_ready.emit(results)


class InstallDependencyWorker(QThread):
    install_finished = pyqtSignal(str, bool)

    def __init__(self, dep_name: str):
        super().__init__()
        self.dep_name = dep_name

    def run(self):
        try:
            res = dependency_manager.install_dependency(self.dep_name)
            self.install_finished.emit(self.dep_name, bool(res))
        except Exception:
            self.install_finished.emit(self.dep_name, False)
