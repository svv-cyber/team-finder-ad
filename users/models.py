from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from users.constants import (
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        verbose_name="Фамилия"
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
        verbose_name="Телефон"
    )
    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub"
    )
    about = models.CharField(
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
        verbose_name="О себе"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Стафф")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


@receiver(pre_save, sender=User)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    """Удаляет файл предыдущего аватара при загрузке нового."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_avatar = old.avatar
    new_avatar = instance.avatar
    if old_avatar and old_avatar != new_avatar:
        old_avatar.delete(save=False)


@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    if instance.avatar:
        instance.avatar.delete(save=False)