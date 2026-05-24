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
    v = value.strip()
    if v.startswith("+7") and len(v) == PHONE_LENGTH_WITH_PLUS_SEVEN:
        return v
    if v.startswith("8") and len(v) == PHONE_LENGTH_WITH_EIGHT:
        return "+7" + v[1:]
    return v