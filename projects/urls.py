from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list, name="list"),
    path("detail/<int:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("create/", views.ProjectCreateView.as_view(), name="create"),
    path("edit/<int:pk>/", views.ProjectUpdateView.as_view(), name="edit"),
    path("complete/<int:pk>/", views.complete_project, name="complete"),
    path(
        "participate/<int:pk>/toggle/",
        views.toggle_participate,
        name="toggle_participate",
    ),
    path("skills/search/", views.skills_autocomplete, name="skills_autocomplete"),
    path("skills/<int:pk>/add/", views.ProjectSkillAddView.as_view(), name="skill_add"),
    path(
        "skills/<int:pk>/remove/<int:skill_id>/",
        views.ProjectSkillRemoveView.as_view(),
        name="skill_remove",
    ),
]
