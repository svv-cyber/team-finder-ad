from django.contrib.auth.models import BaseUserManager

from users.avatar import build_letter_avatar


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть указан email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        content = build_letter_avatar(user.first_name or "?")
        user.avatar.save(content.name, content, save=False)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        if "first_name" not in extra_fields:
            extra_fields["first_name"] = "Admin"
        if "last_name" not in extra_fields:
            extra_fields["last_name"] = "User"

        return self.create_user(email, password, **extra_fields)
