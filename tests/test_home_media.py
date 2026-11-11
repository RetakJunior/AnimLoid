"""Desktop discovery and media loading regression tests."""

import struct
import zlib
from types import SimpleNamespace

from PyQt5.QtCore import QSize

from weeb_cli.gui.workers import ImageLoaderWorker
from weeb_cli.providers import animecix
from weeb_cli.providers.animecix import AnimeCixProvider
from weeb_cli.services import recommendations


def test_recommendations_map_anilist_media_fields():
    media = recommendations._normalise_media([{
        "id": 17,
        "title": {"romaji": "Example", "english": "Example Anime"},
        "coverImage": {"extraLarge": "https://img.test/cover.jpg"},
        "startDate": {"year": 2025},
        "format": "TV",
        "averageScore": 88,
        "genres": ["Action"],
    }])

    assert media[0]["title"] == "Example Anime"
    assert media[0]["cover"] == "https://img.test/cover.jpg"
    assert media[0]["year"] == 2025
    assert media[0]["score"] == 88


def test_recommendations_cache_offline_fallback(monkeypatch):
    calls = []

    def offline(sort, limit):
        calls.append(sort)
        raise OSError("offline")

    monkeypatch.setattr(recommendations, "_cache", {})
    monkeypatch.setattr(recommendations, "_request_recommendations", offline)

    first = recommendations.get_recommendations(force_refresh=True)
    second = recommendations.get_recommendations()

    assert first
    assert all(item["source"] == "offline" for item in first)
    assert second[0]["title"] == first[0]["title"]
    assert calls == ["TRENDING_DESC"]


def test_animecix_details_fetch_each_season_once_then_use_cache(monkeypatch):
    monkeypatch.setattr(animecix, "_EPISODE_CACHE", {})
    monkeypatch.setattr(animecix, "_SEARCH_METADATA", {
        "22": {"name": "Example", "description": "Synopsis", "genres": []},
    })
    calls = []

    def fake_get_json(url, timeout=15):
        calls.append(url)
        if "season=1" in url:
            return {
                "videos": [{"name": "Bölüm 1", "url": "/episode/1", "title": {"seasons": [{}, {}]}}]
            }
        if "season=2" in url:
            return {"videos": [{"name": "Bölüm 2", "url": "/episode/2"}]}
        return None

    monkeypatch.setattr("weeb_cli.providers.animecix._get_json", fake_get_json)
    provider = AnimeCixProvider()

    details = provider.get_details("22")
    episodes = provider.get_episodes("22")

    assert details.title == "Example"
    assert [episode.number for episode in details.episodes] == [1, 2]
    assert [episode.season for episode in episodes] == [1, 2]
    assert len(calls) == 2


def test_animecix_does_not_cache_failed_episode_response(monkeypatch):
    monkeypatch.setattr(animecix, "_EPISODE_CACHE", {})
    monkeypatch.setattr("weeb_cli.providers.animecix._get_json", lambda url, timeout=15: None)

    assert AnimeCixProvider().get_episodes("999") == []
    assert "999" not in animecix._EPISODE_CACHE


def test_image_loader_normalises_url_and_resizes_without_distortion(monkeypatch):
    def chunk(name, data):
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\xff\x00\xff\x00\xff"))
        + chunk(b"IEND", b"")
    )
    monkeypatch.setattr(
        ImageLoaderWorker,
        "_download",
        staticmethod(lambda url: SimpleNamespace(status_code=200, content=png)),
    )
    worker = ImageLoaderWorker("//img.test/poster.png", QSize(32, 48))
    loaded = []
    failed = []
    worker.signals.image_loaded.connect(lambda url, image: loaded.append((url, image.size())))
    worker.signals.image_failed.connect(failed.append)

    worker._load()

    assert not failed
    assert loaded[0][0] == "//img.test/poster.png"
    assert loaded[0][1] == QSize(32, 48)

