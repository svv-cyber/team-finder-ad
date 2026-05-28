from django import forms

from projects.validators import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на репозиторий GitHub",
            "status": "Статус проекта",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"rows": 6, "placeholder": "Описание проекта"}),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/логин/название-репозитория"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = Project.Status.choices

    def clean_github_url(self):
        value = (self.cleaned_data.get("github_url") or "").strip()
        if value:
            github_url_validator(value)
        return value
