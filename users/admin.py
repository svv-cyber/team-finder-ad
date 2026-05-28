from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from users.models import User

AVATAR_SIZE = 40


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "avatar_preview",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {
            "fields": (
                "first_name",
                "last_name",
                "avatar",
                "phone",
                "github_url",
                "about",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "phone",
                "avatar",
                "password1",
                "password2",
            ),
        }),
    )

    @admin.display(description="Фото профиля")
    def avatar_preview(self, obj):
        if not obj.avatar:
            return "—"
        return format_html(
            '<img src="{}" width="{}" height="{}" style="border-radius:50%;object-fit:cover;" />',
            obj.avatar.url,
            AVATAR_SIZE,
            AVATAR_SIZE,
        )
