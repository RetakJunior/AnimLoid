"""Small, cached discovery feed used by the desktop home screen."""

from __future__ import annotations

import threading
import time
from typing import Dict, List


ANILIST_URL = "https://graphql.anilist.co"
CACHE_SECONDS = 30 * 60
SORT_OPTIONS = ("TRENDING_DESC", "POPULARITY_DESC", "SCORE_DESC")

_cache: Dict[str, tuple] = {}
_cache_lock = threading.Lock()

_OFFLINE_TITLES = (
    "Frieren: Beyond Journey's End",
    "Fullmetal Alchemist: Brotherhood",
    "Attack on Titan",
    "Jujutsu Kaisen",
    "Demon Slayer: Kimetsu no Yaiba",
    "Haikyu!!",
)


def _normalise_media(items: list) -> List[dict]:
    results = []
    for item in items:
        title_data = item.get("title") or {}
        title = title_data.get("english") or title_data.get("romaji") or title_data.get("native")
        if not title:
            continue
        cover_data = item.get("coverImage") or {}
        results.append({
            "id": str(item.get("id") or title),
            "slug": str(item.get("id") or title),
            "title": title,
            "name": title,
            "cover": cover_data.get("extraLarge") or cover_data.get("large"),
            "year": (item.get("startDate") or {}).get("year"),
            "type": (item.get("format") or "ANIME").replace("_", " ").title(),
            "score": item.get("averageScore"),
            "genres": item.get("genres") or [],
            "source": "anilist",
        })
    return results


def _request_recommendations(sort: str, limit: int) -> List[dict]:
    query = """
    query ($sort: [MediaSort], $pageSize: Int) {
      Page(page: 1, perPage: $pageSize) {
        media(type: ANIME, sort: $sort, isAdult: false) {
          id
          title { romaji english native }
          coverImage { extraLarge large }
          startDate { year }
          format
          averageScore
          genres
        }
      }
    }
    """
    payload = {"query": query, "variables": {"sort": [sort], "pageSize": limit}}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    try:
        from curl_cffi import requests as http
        response = http.post(ANILIST_URL, json=payload, headers=headers, timeout=12, impersonate="chrome120")
    except ImportError:
        import requests as http
        response = http.post(ANILIST_URL, json=payload, headers=headers, timeout=12)
    response.raise_for_status()
    data = response.json()
    media = data.get("data", {}).get("Page", {}).get("media", [])
    return _normalise_media(media)


def get_recommendations(sort: str = "TRENDING_DESC", limit: int = 12, force_refresh: bool = False) -> List[dict]:
    """Return a cached trend list, falling back to searchable titles offline."""
    sort = sort if sort in SORT_OPTIONS else SORT_OPTIONS[0]
    limit = max(1, min(int(limit), 24))
    now = time.monotonic()

    with _cache_lock:
        cached = _cache.get(sort)
        if not force_refresh and cached and now - cached[0] < CACHE_SECONDS:
            return [dict(item) for item in cached[1][:limit]]

    try:
        items = _request_recommendations(sort, limit)
    except Exception:
        items = []

    if items:
        with _cache_lock:
            _cache[sort] = (now, items)
        return [dict(item) for item in items[:limit]]

    # Keep the home screen useful when the recommendation API is offline.
    # Cache the fallback too so returning home does not repeatedly hit a dead API.
    items = [
        {"id": title, "slug": title, "title": title, "name": title, "cover": None, "type": "Anime", "source": "offline"}
        for title in _OFFLINE_TITLES[:limit]
    ]
    with _cache_lock:
        _cache[sort] = (now, items)
    return [dict(item) for item in items]
