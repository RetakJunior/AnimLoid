"""Provider response parsing tests. All HTTP boundaries are mocked."""

from weeb_cli.exceptions import ProviderError
from weeb_cli.providers.allanime import AllAnimeProvider
from weeb_cli.providers.animecix import AnimeCixProvider
from weeb_cli.providers.anizle import AnizleProvider
from weeb_cli.providers.hianime import HiAnimeProvider
from weeb_cli.providers.turkanime import TurkAnimeProvider


def test_animecix_search_maps_catalogue_response(monkeypatch):
    monkeypatch.setattr(
        "weeb_cli.providers.animecix._get_json",
        lambda url: {"results": [{"id": 22, "name": "Example", "episode_count": 12}]},
    )

    result = AnimeCixProvider().search("Example")[0]

    assert result.id == "22"
    assert result.title == "Example"
    assert result.playable is True


def test_animecix_search_reports_transport_failure(monkeypatch):
    monkeypatch.setattr("weeb_cli.providers.animecix._get_json", lambda url: None)

    try:
        AnimeCixProvider().search("Example")
    except ProviderError as exc:
        assert exc.code == "PROVIDER_UNAVAILABLE"
    else:
        raise AssertionError("a failed provider request should be reported")


def test_turkanime_search_parses_title_and_poster(monkeypatch):
    def fake_fetch(path, *args, **kwargs):
        if path.startswith("/anime/"):
            return '<title>Naruto izle | TurkAnime</title><meta property="og:image" content="https://img.test/naruto.jpg">'
        return "<html></html>"

    monkeypatch.setattr("weeb_cli.providers.turkanime._fetch", fake_fetch)

    result = TurkAnimeProvider().search("Naruto")[0]

    assert result.id == "naruto"
    assert result.title == "Naruto"
    assert result.cover == "https://img.test/naruto.jpg"


def test_turkanime_reports_lander_instead_of_no_results(monkeypatch):
    monkeypatch.setattr(
        "weeb_cli.providers.turkanime._fetch",
        lambda path, *args, **kwargs: '<script>window.location.href="/lander?arama=naruto"</script>',
    )

    try:
        TurkAnimeProvider().search("Naruto")
    except ProviderError as exc:
        assert exc.code == "PROVIDER_UNAVAILABLE"
    else:
        raise AssertionError("a redirect landing page should be reported as unavailable")


def test_anizle_search_maps_catalogue_records(monkeypatch):
    monkeypatch.setattr(
        "weeb_cli.providers.anizle._load_database",
        lambda: [{"info_slug": "example", "info_title": "Example Anime", "info_year": "2024", "info_poster": "https://img.test/example.jpg"}],
    )
    monkeypatch.setattr("weeb_cli.providers.anizle._resolve_anilist_posters", lambda items: None)

    result = AnizleProvider().search("Example Anime")[0]

    assert result.id == "example"
    assert result.title == "Example Anime"
    assert result.year == 2024


def test_anizle_search_reports_unavailable_catalogue(monkeypatch):
    monkeypatch.setattr("weeb_cli.providers.anizle._load_database", lambda: [])
    monkeypatch.setattr("weeb_cli.providers.anizle._database_loaded", False)

    try:
        AnizleProvider().search("Example")
    except ProviderError as exc:
        assert exc.code == "PROVIDER_UNAVAILABLE"
    else:
        raise AssertionError("an unavailable catalogue should be reported")


def test_hianime_search_parses_result_card(monkeypatch):
    html = '''<div class="flw-item"><div class="film-name"><a class="dynamic-name" href="/watch/example-123">Example Anime</a></div>
      <img class="film-poster-img" data-src="https://img.test/example.jpg"><span class="fdi-item">TV</span></div>'''
    monkeypatch.setattr("weeb_cli.providers.hianime._get_html", lambda *args, **kwargs: html)

    result = HiAnimeProvider().search("Example")[0]

    assert result.id == "example-123"
    assert result.title == "Example Anime"
    assert result.cover == "https://img.test/example.jpg"


def test_allanime_search_details_episodes_and_streams(monkeypatch):
    provider = AllAnimeProvider()
    monkeypatch.setattr(
        "weeb_cli.providers.allanime._graphql_request",
        lambda query, variables: {
            "data": {
                "shows": {"edges": [{"_id": "example", "name": "Example Anime", "availableEpisodes": {"sub": 2}}]},
                "show": {"_id": "example", "name": "Example Anime", "description": "Synopsis", "thumbnail": "https://img.test/example.jpg", "availableEpisodesDetail": {"sub": ["2", "1"]}},
                "episode": {"sourceUrls": [{"sourceUrl": "--encoded", "sourceName": "Vidstream"}]},
            }
        },
    )
    monkeypatch.setattr("weeb_cli.providers.allanime._decode_provider_id", lambda value: "/clock")
    monkeypatch.setattr("weeb_cli.providers.allanime._get_json", lambda *args, **kwargs: {"links": [{"link": "https://cdn.test/video.m3u8", "resolutionStr": "1080p"}]})

    found = provider.search("Example")
    details = provider.get_details("example")
    episodes = provider.get_episodes("example")
    streams = provider.get_streams("example", "example::ep=1")

    assert found[0].id == "example"
    assert details.title == "Example Anime"
    assert [episode.title for episode in episodes] == ["Episode 1", "Episode 2"]
    assert streams[0].url == "https://cdn.test/video.m3u8"
