import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError

GITHUB_HOST = "github.com"
GITHUB_PATTERN = re.compile(r"github\.com/[\w\-]+/[\w\-]+")

PHONE_LENGTH_WITH_PLUS_SEVEN = 12
PHONE_LENGTH_WITH_EIGHT = 11


def github_url_validator(value: str) -> None:
    if not value:
        return
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if GITHUB_HOST not in host:
        raise ValidationError("Ссылка должна вести на GitHub.", code="invalid_github")
    if not GITHUB_PATTERN.search(value):
        raise ValidationError(
            "Ссылка должна указывать на конкретный репозиторий (username/repo).",
            code="invalid_repo"
        )


def normalize_phone_digits(value: str) -> str:
    normalized_value = value.strip()
    if normalized_value.startswith("+7") and len(normalized_value) == PHONE_LENGTH_WITH_PLUS_SEVEN:
        return normalized_value
    if normalized_value.startswith("8") and len(normalized_value) == PHONE_LENGTH_WITH_EIGHT:
        return "+7" + normalized_value[1:]
    return normalized_value
