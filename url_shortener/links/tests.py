from django.test import TestCase

import pytest

from .models import ShortenedURL 
pytestmark = pytest.mark.django_db


class TestShortenedURLModel:
    def test_deleting_user_does_not_delete_urls(self, user):
        url = ShortenedURL.objects.create(
            short_code="abc123",
            long_url="https://example.com",
            created_by=user,
        )
        user.delete()
        url.refresh_from_db()
        assert url.created_by is None
