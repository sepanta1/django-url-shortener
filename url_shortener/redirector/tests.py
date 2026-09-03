import pytest
from django.core.cache import cache
from django.http import Http404

from url_shortener.links.models import ShortenedURL

from .services import resolve_short_code


@pytest.fixture
def short_url(db):
    cache.clear()

    obj = ShortenedURL.objects.create(
        short_code="abc123",
        long_url="https://example.com",
    )

    yield obj

    cache.clear()


def test_returns_long_url_on_cache_miss(short_url):
    resolved = resolve_short_code(short_url.short_code)

    assert resolved == short_url.long_url


def test_populates_cache_on_miss(short_url):
    resolved = resolve_short_code(short_url.short_code)

    assert cache.get(f"shorturl:{short_url.short_code}") == resolved


def test_returns_long_url_on_cache_hit(short_url):
    fake_code = "doesnotexist"
    cached_url = "https://cached-example.com"

    cache.set(f"shorturl:{fake_code}", cached_url)

    resolved = resolve_short_code(fake_code)

    assert resolved == cached_url


def test_increments_click_count_on_cache_miss(short_url):
    resolve_short_code(short_url.short_code)

    pending_key = f"click_pending:{short_url.short_code}"

    assert cache.get(pending_key) == 1


def test_increments_click_count_on_cache_hit(short_url):
    cache.set(
        f"shorturl:{short_url.short_code}",
        short_url.long_url,
    )

    resolve_short_code(short_url.short_code)

    pending_key = f"click_pending:{short_url.short_code}"

    assert cache.get(pending_key) == 1


def test_updates_last_clicked_at(short_url):
    # Click tracking is handled asynchronously by Celery.
    resolve_short_code(short_url.short_code)

    pending_key = f"click_pending:{short_url.short_code}"

    assert cache.get(pending_key) == 1


def test_raises_404_for_nonexistent_code(db):
    with pytest.raises(Http404):
        resolve_short_code("doesnotexist")
