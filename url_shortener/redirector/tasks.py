from celery import shared_task
from django.core.cache import cache
from django.db.models import F
from django.utils import timezone

from url_shortener.links.models import ShortenedURL

from .services import CLICK_COUNTER_PREFIX


@shared_task
def flush_click_counts():
    """
    Flush pending Redis click counters into PostgreSQL.
    """

    pending_keys = cache.keys(f"{CLICK_COUNTER_PREFIX}*")

    for key in pending_keys:
        short_code = key.replace(
            CLICK_COUNTER_PREFIX,
            "",
            1,
        )

        count = cache.get(key)

        if not count:
            continue

        ShortenedURL.objects.filter(pk=short_code).update(
            click_count=F("click_count") + count,
            last_clicked_at=timezone.now(),
        )

        cache.delete(key)
