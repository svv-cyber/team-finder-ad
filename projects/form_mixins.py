from projects.validators import github_url_validator


class GithubUrlCleanMixin:

    def clean_github_url(self):
        value = (self.cleaned_data.get("github_url") or "").strip()
        if value:
            github_url_validator(value)
        return value