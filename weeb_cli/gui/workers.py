"""Asynchronous workers and background threads for AnimLoid GUI."""

import os
import urllib.request
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QImage

from weeb_cli.config import config
from weeb_cli.providers import get_provider
from weeb_cli.services.scraper import scraper
from weeb_cli.services.details import get_details
from weeb_cli.services.watch import get_streams
from weeb_cli.services.player import player
from weeb_cli.services.dependency_manager import dependency_manager
from weeb_cli.services.downloader import queue_manager

_IMAGE_CACHE: dict = {}


class ImageLoaderWorker(QThread):
    """Load a remote image in a QThread safely using QImage."""
    image_loaded = pyqtSignal(str, QImage)
    image_failed = pyqtSignal(str)

    def __init__(self, url: str, target_size=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.target_size = target_size

    def run(self):
        if not self.url:
            self.image_failed.emit(self.url or "")
            return

        if self.url in _IMAGE_CACHE:
            cached_img = _IMAGE_CACHE[self.url]
            if not cached_img.isNull():
                self.image_loaded.emit(self.url, cached_img)
                return

        content = None
        # 1) Try curl_cffi
        try:
            from curl_cffi import requests as cr
            resp = cr.get(self.url, impersonate="chrome120", timeout=8)
            if resp.status_code == 200:
                content = resp.content
        except Exception:
            pass

        # 2) Fallback urllib
        if content is None:
            try:
                req = urllib.request.Request(
                    self.url,
                    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
                )
                with urllib.request.urlopen(req, timeout=8) as r:
                    content = r.read()
            except Exception:
                pass

        if content:
            image = QImage()
            if image.loadFromData(content):
                _IMAGE_CACHE[self.url] = image
                self.image_loaded.emit(self.url, image)
                return

        self.image_failed.emit(self.url)




class SearchWorker(QThread):
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, query: str, source_name: str = None):
        super().__init__()
        self.query = query
        self.source_name = source_name

    def run(self):
        try:
            if self.source_name:
                config.set("scraping_source", self.source_name)
            
            results = scraper.search(self.query)
            
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
                        })
                    elif isinstance(r, dict):
                        formatted_results.append(r)
            
            self.results_ready.emit(formatted_results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DetailsWorker(QThread):
    details_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, slug: str, source_name: str = None):
        super().__init__()
        self.slug = slug
        self.source_name = source_name

    def run(self):
        try:
            if self.source_name:
                config.set("scraping_source", self.source_name)

            details = get_details(self.slug)
            if details:
                self.details_ready.emit(details)
            else:
                self.error_occurred.emit("Anime detayları alınamadı veya kaynak yanıt vermedi.")
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
            if self.source_name:
                config.set("scraping_source", self.source_name)

            stream_data = get_streams(self.anime_id, self.episode_id)
            if stream_data and "data" in stream_data and "links" in stream_data["data"]:
                links = stream_data["data"]["links"]
                self.streams_ready.emit(links)
            else:
                self.error_occurred.emit("Yayın bağlantısı bulunamadı.")
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

