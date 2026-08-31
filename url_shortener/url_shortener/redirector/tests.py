from django.core.cache import cache
from django.test import TestCase

from url_shortener.links.models import ShortenedURL

from .services import resolve_short_code


class TestResolveShortCode(TestCase):
    def setUp(self):
        cache.clear()
        self.obj = ShortenedURL.objects.create(
            short_code="abc123",
            long_url="https://example.com",
        )

    def test_returns_long_url_on_cache_miss(self):
        resolved = resolve_short_code(self.obj.short_code)
        long_url = self.obj.long_url
        assert long_url == resolved

    def test_populates_cache_on_miss(self):
        resolved = resolve_short_code(self.obj.short_code)
        assert cache.get(f"shorturl:{self.obj.short_code}") == resolved

    def test_returns_long_url_on_cache_hit(self):
        fake_code = "doesnotexist"
        cached_url = "https://cached-example.com"
        cache.set(f"shorturl:{fake_code}", cached_url)
        resolved = resolve_short_code(fake_code)
        assert resolved == cached_url

    def test_increments_click_count_on_cache_miss(self):
        click_count_old = self.obj.click_count

        resolve_short_code(self.obj.short_code)

        self.obj.refresh_from_db()
        click_count_new = self.obj.click_count

        assert click_count_new == click_count_old + 1

    def test_increments_click_count_on_cache_hit(self):
        cache.set(f"shorturl:{self.obj.short_code}", self.obj.long_url)
        click_count_old = self.obj.click_count

        resolve_short_code(self.obj.short_code)

        self.obj.refresh_from_db()
        assert self.obj.click_count == click_count_old + 1

    def test_updates_last_clicked_at(self):
        assert self.obj.last_clicked_at is None

        resolve_short_code(self.obj.short_code)

        self.obj.refresh_from_db()
        assert self.obj.last_clicked_at is not None

    def test_raises_404_for_nonexistent_code(self):
        from django.http import Http404

        with self.assertRaises(Http404):
            resolve_short_code("doesnotexist")
