from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from django.db import IntegrityError

from .services import _base62_encode
from .services import create_short_url
from .services import generate_short_code


class TestBase62Encode:
    def test_zero_returns_first_char(self):
        assert _base62_encode(0) == "0"

    def test_encodes_known_value(self):
        # 61 is the last index in the alphabet (0-9a-zA-Z), so it should be "Z"
        assert _base62_encode(61) == "Z"

    def test_encodes_larger_number(self):
        result = _base62_encode(12345)
        assert isinstance(result, str)
        assert result != ""


class TestGenerateShortCode:
    def test_same_url_produces_same_code(self):
        code1 = generate_short_code("https://example.com")
        code2 = generate_short_code("https://example.com")
        assert code1 == code2

    def test_different_urls_produce_different_codes(self):
        code1 = generate_short_code("https://example.com")
        code2 = generate_short_code("https://different.com")
        assert code1 != code2

    def test_salt_changes_output(self):
        code1 = generate_short_code("https://example.com", salt="")
        code2 = generate_short_code("https://example.com", salt="123")
        assert code1 != code2

    def test_code_length_is_six(self):
        code = generate_short_code("https://example.com")
        assert len(code) == 6


class TestCreateShortUrl:
    @patch("url_shortener.shortener.services.transaction.atomic")
    def test_creates_url_when_no_collision(self, mock_atomic):
        mock_model = MagicMock()

        code = create_short_url("https://example.com", mock_model)

        mock_model.objects.create.assert_called_once_with(
            short_code=code,
            long_url="https://example.com",
            created_by=None,
        )

    @patch("url_shortener.shortener.services.transaction.atomic")
    def test_retries_on_collision_then_succeeds(self, mock_atomic):
        mock_model = MagicMock()

        mock_model.objects.create.side_effect = [
            IntegrityError,
            None,
        ]

        code = create_short_url("https://example.com", mock_model)

        assert mock_model.objects.create.call_count == 2
        assert isinstance(code, str)

    @patch("url_shortener.shortener.services.transaction.atomic")
    def test_raises_after_max_retries_exhausted(self, mock_atomic):
        mock_model = MagicMock()
        mock_model.objects.create.side_effect = IntegrityError

        with pytest.raises(RuntimeError):
            create_short_url("https://example.com", mock_model)

        assert mock_model.objects.create.call_count == 3
