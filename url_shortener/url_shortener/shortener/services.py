import hashlib
import string

from django.utils import timezone

BASE62_ALPHABET = string.digits + string.ascii_letters
CODE_LENGTH = 6
MAX_RETRIES = 3


def _base62_encode(value: int) -> str:
    if value == 0:
        return BASE62_ALPHABET[0]
    chars = []
    base = len(BASE62_ALPHABET)
    while value > 0:
        value, remainder = divmod(value, base)
        chars.append(BASE62_ALPHABET[remainder])
    return "".join(reversed(chars))


def generate_short_code(long_url: str, salt: str = "") -> str:
    """Hash the URL (optional salt for retries) and base62-encode a slice of it."""
    # sha256 doesn't directly support str!
    # we need to turn it into bytes using encode
    # and then to a hexadecimal str using hexdigest
    digest = hashlib.sha256(f"{long_url}{salt}".encode()).hexdigest()
    # take first 6 hex chars, convert to int, then base62-encode
    number = int(digest[:CODE_LENGTH], 16)
    code = _base62_encode(number)
    return code.rjust(CODE_LENGTH, BASE62_ALPHABET[0])[:CODE_LENGTH]


def create_short_url(long_url: str, model, user=None) -> str:
    """
    model: your ShortenedURL model, passed in to keep this function
    decoupled from Django ORM specifics if you ever want to test it standalone.
    """
    for attempt in range(MAX_RETRIES):
        salt = "" if attempt == 0 else str(timezone.now().timestamp())
        code = generate_short_code(long_url, salt=salt)
        if not model.objects.filter(short_code=code).exists():
            model.objects.create(
                short_code=code,
                long_url=long_url,
                created_by=user if user and user.is_authenticated else None,
            )
            return code
    raise RuntimeError("Failed to generate a unique short code after shoretries")
