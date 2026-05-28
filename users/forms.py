from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

from projects.validators import validate_github_url
from users.constants import (
    AVATAR_MAX_SIZE_BYTES,
    AVATAR_MAX_SIZE_MB,
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from users.validators import validate_phone

User = get_user_model()


class RegisterForm(forms.Form):
    first_name = forms.CharField(label="Имя", max_length=USER_NAME_MAX_LENGTH)
    last_name = forms.CharField(label="Фамилия", max_length=USER_SURNAME_MAX_LENGTH)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"].strip().lower()
        return User.objects.create_user(
            email=email,
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "avatar", "about", "phone", "github_url")

    def clean_github_url(self):
        value = (self.cleaned_data.get("github_url") or "").strip()
        if value:
            validate_github_url(value)
        return value

    def clean_phone(self):
        return validate_phone(
            self.cleaned_data.get("phone"),
            exclude_user=self.instance.pk
        )

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > AVATAR_MAX_SIZE_BYTES:
                raise forms.ValidationError(
                    f"Размер аватара не должен превышать {AVATAR_MAX_SIZE_MB}MB."
                )
            ext = avatar.name.split(".")[-1].lower()
            allowed = ("jpg", "jpeg", "png", "gif", "avif")
            if ext not in allowed:
                raise forms.ValidationError("Поддерживаются только JPG, PNG, GIF.")
        return avatar


class UserPasswordChangeForm(PasswordChangeForm):
    pass