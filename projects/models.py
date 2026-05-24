from django.conf import settings
from django.db import models
from django.urls import reverse

from projects.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
)


class Skill(models.Model):
    name = models.CharField(
        max_length=SKILL_NAME_MAX_LENGTH,
        unique=True,
        verbose_name="Название навыка"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    name = models.CharField(
        max_length=PROJECT_NAME_MAX_LENGTH,
        verbose_name="Название проекта"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Владелец"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub ссылка"
    )
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name="Статус"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники"
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="projects",
        blank=True,
        verbose_name="Навыки"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})