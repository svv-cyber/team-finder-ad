import re
from django.core.exceptions import ValidationError
from users.models import User
from projects.validators import normalize_phone_digits

PHONE_PATTERN = re.compile(r"^(?:\+7|8)\d{10}$")


def validate_phone(value, exclude_user=None):
    """Валидация и нормализация номера телефона"""
    raw = (value or "").strip()
    if not raw:
        return ""
    if not PHONE_PATTERN.match(raw):
        raise ValidationError(
            "Допустимые форматы: 8XXXXXXXXXX или +7XXXXXXXXXX. "
            "Пример: 89123456789 или +79123456789"
        )
    normalized = normalize_phone_digits(raw)
    taken = User.objects.exclude(pk=exclude_user).exclude(phone="").filter(phone=normalized).exists()
    if taken:
        raise ValidationError("Этот номер уже занят другим пользователем.")
    return normalized