import json
import time
import threading
import urllib.request
from urllib.parse import urlparse, parse_qs, quote, urlsplit, urlunsplit
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from weeb_cli.providers.base import (
    BaseProvider,
    AnimeResult,
    AnimeDetails,
    Episode,
    StreamLink
)
from weeb_cli.providers.registry import register_provider
from weeb_cli.exceptions import ProviderError

BASE_URL = "https://animecix.tv/"
ALT_URL = "https://mangacix.net/"
VIDEO_PLAYERS = ["tau-video.xyz", "sibnet"]
# The search endpoint already carries the reliable catalogue metadata.  The
# legacy details endpoint frequently returns empty data (and /titles/{id} can
# even return a different title), so retain this small in-process lookup for
# the detail request that immediately follows a search result click.
_SEARCH_METADATA = {}
_EPISODE_CACHE = {}
_EPISODE_CACHE_LOCK = threading.Lock()
_EPISODE_CACHE_SECONDS = 5 * 60
_EPISODE_CACHE_LIMIT = 128

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def _http_get(url: str, timeout: int = 15) -> bytes:
    sp = urlsplit(url)
    safe_path = quote(sp.path, safe="/:%@")
    safe_url = urlunsplit((sp.scheme, sp.netloc, safe_path, sp.query, sp.fragment))
    
    try:
        from curl_cffi import requests as curl_requests
        resp = curl_requests.get(safe_url, headers={"Accept": "application/json"}, impersonate="chrome120", timeout=timeout)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        pass

    req = urllib.request.Request(safe_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _get_json(url: str, timeout: int = 15):
    try:
        data = _http_get(url, timeout)
        return json.loads(data)
    except Exception:
        return None


@register_provider("animecix", lang="tr", region="TR")
class AnimeCixProvider(BaseProvider):
    
    def __init__(self):
        super().__init__()
        
    def search(self, query: str) -> List[AnimeResult]:
        q = (query or "").strip().replace(" ", "-")
        q_enc = quote(q, safe="-")
        url = f"{BASE_URL}secure/search/{q_enc}?type=&limit=20"
        
        data = _get_json(url)
        if data is None:
            raise ProviderError("AnimeCix arama servisine bağlanılamadı.", "PROVIDER_UNAVAILABLE")
        if "results" not in data:
            return []
        
        results = []
        for item in data["results"]:
            name = item.get("name")
            _id = item.get("id")
            if name and _id:
                _SEARCH_METADATA[str(_id)] = item
                results.append(AnimeResult(
                    id=str(_id),
                    title=str(name),
                    type=self._parse_type(item.get("title_type") or item.get("type", "")),
                    cover=item.get("poster") or None,
                    year=item.get("year") or None,
                    # AnimeCix returns catalogue-only films alongside actual
                    # streams.  Do not pretend those records can be played.
                    playable=bool(item.get("episode_count")),
                ))
        
        return results
    
    def get_details(self, anime_id: str) -> Optional[AnimeDetails]:
        try:
            safe_id = int(anime_id)
        except (ValueError, TypeError):
            return None
        title_data = _SEARCH_METADATA.get(str(safe_id))
        cached_episodes = self._cached_episodes(safe_id)
        data = None
        if cached_episodes is None or not title_data:
            url = f"{ALT_URL}secure/related-videos?episode=1&season=1&titleId={safe_id}&videoId=637113"
            data = _get_json(url)
        if data and "videos" in data:
            videos = data.get("videos") or []
            if videos and not title_data:
                title_data = videos[0].get("title")
        
        episodes = cached_episodes if cached_episodes is not None else self._get_episodes_from_data(safe_id, data)
        
        if not title_data:
            return AnimeDetails(
                id=anime_id,
                title=anime_id,
                episodes=episodes,
                total_episodes=len(episodes)
            )
        
        return AnimeDetails(
            id=anime_id,
            title=title_data.get("name", ""),
            description=title_data.get("description"),
            cover=title_data.get("poster"),
            genres=[g.get("name", "") for g in title_data.get("genres", []) if g.get("name")],
            year=title_data.get("year"),
            episodes=episodes,
            total_episodes=len(episodes)
        )
    
    def get_episodes(self, anime_id: str) -> List[Episode]:
        try:
            safe_id = int(anime_id)
        except (ValueError, TypeError):
            return []

        cached = self._cached_episodes(safe_id)
        if cached is not None:
            return cached
        
        first_url = f"{ALT_URL}secure/related-videos?episode=1&season=1&titleId={safe_id}&videoId=637113"
        return self._get_episodes_from_data(safe_id, _get_json(first_url))

    @staticmethod
    def _cached_episodes(title_id: int) -> Optional[List[Episode]]:
        with _EPISODE_CACHE_LOCK:
            cached = _EPISODE_CACHE.get(str(title_id))
            if cached and time.monotonic() - cached[0] < _EPISODE_CACHE_SECONDS:
                return list(cached[1])
        return None

    def _get_episodes_from_data(self, title_id: int, first_data) -> List[Episode]:
        cache_key = str(title_id)
        now = time.monotonic()
        cached = self._cached_episodes(title_id)
        if cached is not None:
            return cached

        seasons = self._get_seasons_from_data(first_data)
        if not seasons:
            seasons = [0]

        payloads = {0: first_data}
        other_seasons = seasons[1:]
        if other_seasons:
            def fetch_season(sidx):
                url = f"{ALT_URL}secure/related-videos?episode=1&season={sidx+1}&titleId={title_id}&videoId=637113"
                return sidx, _get_json(url)

            with ThreadPoolExecutor(max_workers=min(4, len(other_seasons))) as pool:
                for sidx, data in pool.map(fetch_season, other_seasons):
                    payloads[sidx] = data

        episodes = []
        seen = set()
        for sidx in seasons:
            data = payloads.get(sidx)
            if not data or "videos" not in data:
                continue
            for video in data.get("videos") or []:
                name = video.get("name")
                episode_url = video.get("url")
                if not name or not episode_url or episode_url in seen:
                    continue
                seen.add(episode_url)
                episodes.append(Episode(
                    id=episode_url,
                    number=self._parse_episode_number(name, len(episodes) + 1),
                    title=name,
                    season=sidx + 1,
                    url=episode_url,
                ))

        episodes.sort(key=lambda episode: (episode.season, episode.number))
        complete = (
            isinstance(first_data, dict)
            and "videos" in first_data
            and all(
                isinstance(payloads.get(season_index), dict)
                and "videos" in payloads[season_index]
                for season_index in seasons
            )
        )
        if complete:
            with _EPISODE_CACHE_LOCK:
                _EPISODE_CACHE[cache_key] = (now, list(episodes))
                if len(_EPISODE_CACHE) > _EPISODE_CACHE_LIMIT:
                    oldest_key = min(_EPISODE_CACHE, key=lambda key: _EPISODE_CACHE[key][0])
                    _EPISODE_CACHE.pop(oldest_key, None)
        return episodes
    
    def get_streams(self, anime_id: str, episode_id: str) -> List[StreamLink]:
        embed_path = episode_id.lstrip("/")
        
        if embed_path.startswith("http"):
            full_url = embed_path
        else:
            full_url = f"{BASE_URL}{quote(embed_path, safe='/:?=&')}"
        
        try:
            from curl_cffi import requests as curl_requests
            # Use curl_cffi to follow Cloudflare-protected redirects
            resp = curl_requests.get(full_url, impersonate="chrome120", timeout=15, allow_redirects=True)
            final_url = resp.url
            
            p = urlparse(final_url)
            parts = p.path.strip("/").split("/")
            
            embed_id = None
            if len(parts) >= 2:
                if parts[0] == "embed":
                    embed_id = parts[1]
                else:
                    embed_id = parts[0]
            elif len(parts) == 1 and parts[0]:
                embed_id = parts[0]
            
            qs = parse_qs(p.query)
            vid = (qs.get("vid") or [None])[0]
            
            if not embed_id or not vid:
                return []
            
            api_url = f"https://{VIDEO_PLAYERS[0]}/api/video/{embed_id}?vid={vid}"
            api_resp = curl_requests.get(api_url, impersonate="chrome120", timeout=15, headers={"Referer": final_url})
            
            if api_resp.status_code != 200:
                return []
            
            video_data = api_resp.json()
            if not video_data or "urls" not in video_data:
                return []
            
            streams = []
            for u in video_data["urls"]:
                label = u.get("label")
                url = u.get("url")
                if url:
                    streams.append(StreamLink(
                        url=url,
                        quality=label or "auto",
                        server="tau-video"
                    ))
            
            return streams
            
        except Exception:
            return []
    
    def _get_seasons(self, title_id: int) -> List[int]:
        try:
            safe_id = int(title_id)
        except (ValueError, TypeError):
            return [0]
        
        url = f"{ALT_URL}secure/related-videos?episode=1&season=1&titleId={safe_id}&videoId=637113"
        return self._get_seasons_from_data(_get_json(url))

    @staticmethod
    def _get_seasons_from_data(data) -> List[int]:
        if not data or "videos" not in data:
            return [0]
        
        videos = data.get("videos") or []
        if not videos:
            return [0]
        
        title = (videos[0] or {}).get("title") or {}
        if not isinstance(title, dict):
            return [0]
        seasons = title.get("seasons") or []
        
        if seasons:
            return list(range(len(seasons)))
        return [0]
    
    def _parse_type(self, title_type: str) -> str:
        title_type = (title_type or "").lower()
        if "movie" in title_type or "film" in title_type:
            return "movie"
        if "ova" in title_type:
            return "ova"
        return "series"
    
    def _parse_episode_number(self, name: str, fallback: int) -> int:
        import re
        patterns = [
            r'(?:bölüm|episode|ep)\s*(\d+)',
            r'(\d+)\.\s*(?:bölüm|episode)',
            r'^(\d+)$'
        ]
        
        name_lower = name.lower()
        for pattern in patterns:
            match = re.search(pattern, name_lower)
            if match:
                return int(match.group(1))
        
        return fallback
