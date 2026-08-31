from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone

from url_shortener.links.models import ShortenedURL

CACHE_TTL_SECONDS = 60 * 60 * 24
CLICK_COUNTER_PREFIX = "click_pending:"


def resolve_short_code(short_code: str) -> str:
    """
    Look up the long URL for a short code, track the click,
    and return the long URL for redirecting to.
    """
    cache_key = f"shorturl:{short_code}"
    long_url = cache.get(cache_key)

    if long_url is None:
        obj = get_object_or_404(ShortenedURL, pk=short_code)
        long_url = obj.long_url
        cache.set(cache_key, long_url, CACHE_TTL_SECONDS)
    else:
        obj = None
    _track_click(short_code)
    return long_url


def _track_click(short_code: str) -> None:

    key = f"{CLICK_COUNTER_PREFIX}{short_code}"
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1)
