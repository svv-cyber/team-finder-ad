import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from projects.constants import PROJECTS_PER_PAGE, SKILL_AUTOCOMPLETE_LIMIT
from projects.forms import ProjectForm
from projects.mixins import OwnerOrStaffMixin
from projects.models import Project, Skill
from projects.services import (add_project_participant, is_project_participant,
                               remove_project_participant)
from users.services import paginate_queryset


def root_redirect(request):
    return redirect("projects:list")


def project_list(request):
    queryset = (
        Project.objects.select_related("owner")
        .prefetch_related("participants", "skills")
    )
    active_skill = (request.GET.get("skill") or "").strip()
    if active_skill:
        queryset = queryset.filter(skills__name=active_skill).distinct()
    all_skills = Skill.objects.all()
    page_obj = paginate_queryset(request, queryset, PROJECTS_PER_PAGE)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related("owner").prefetch_related(
            "participants", "skills"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        project = self.object
        context["is_participant"] = is_project_participant(project, user)
        context["is_owner"] = user == project.owner
        context["participants_count"] = project.participants.count()
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        add_project_participant(self.object, self.request.user)
        return response

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, OwnerOrStaffMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})


@login_required
def complete_project(request, pk):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=pk)

    is_allowed = (
        request.user.is_staff or project.owner_id == request.user.id
    ) and project.status == Project.Status.OPEN

    if not is_allowed:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    project.status = Project.Status.CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": Project.Status.CLOSED})


@login_required
def toggle_participate(request, pk):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=pk)

    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)

    user = request.user
    if is_project_participant(project, user):
        remove_project_participant(project, user)
        is_participant = False
    else:
        add_project_participant(project, user)
        is_participant = True

    return JsonResponse({"status": "ok", "participant": is_participant})


def skills_autocomplete(request):
    query = (request.GET.get("q") or "").strip()
    queryset = Skill.objects.all()
    if query:
        queryset = queryset.filter(name__istartswith=query)
    queryset = queryset[:SKILL_AUTOCOMPLETE_LIMIT]
    data = [{"id": skill.pk, "name": skill.name} for skill in queryset]
    return JsonResponse(data, safe=False)


@method_decorator(login_required, name="dispatch")
class ProjectSkillAddView(View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        if not (request.user.is_staff or project.owner_id == request.user.id):
            return JsonResponse({"error": "forbidden"}, status=HTTPStatus.FORBIDDEN)

        payload = {}
        if request.body:
            try:
                payload = json.loads(request.body.decode())
            except json.JSONDecodeError:
                payload = {}

        skill_id = payload.get("skill_id") or request.POST.get("skill_id")
        if skill_id is not None:
            skill_id = str(skill_id).strip()
            try:
                skill_id = int(skill_id)
            except (TypeError, ValueError):
                skill_id = None

        name = (payload.get("name") or request.POST.get("name") or "").strip()

        created = False
        added = False
        skill = None

        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        elif name:
            with transaction.atomic():
                skill, created = Skill.objects.get_or_create(
                    name__iexact=name,
                    defaults={"name": name}
                )
                if not created and skill.name != name:
                    skill.name = name
                    skill.save()
        else:
            return JsonResponse(
                {"skill_id": None, "created": False, "added": False},
                status=HTTPStatus.BAD_REQUEST,
            )

        if skill and project.skills.filter(pk=skill.pk).exists():
            return JsonResponse(
                {
                    "skill_id": skill.pk,
                    "name": skill.name,
                    "created": created,
                    "added": False,
                }
            )

        if skill:
            project.skills.add(skill)
            added = True

        return JsonResponse(
            {
                "skill_id": skill.pk,
                "name": skill.name,
                "created": created,
                "added": added,
            }
        )


@method_decorator(login_required, name="dispatch")
class ProjectSkillRemoveView(View):
    def post(self, request, pk, skill_id):
        project = get_object_or_404(Project, pk=pk)

        if not (request.user.is_staff or project.owner_id == request.user.id):
            return JsonResponse({"error": "forbidden"}, status=HTTPStatus.FORBIDDEN)

        skill = get_object_or_404(Skill, pk=skill_id)

        if not project.skills.filter(pk=skill.pk).exists():
            return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)

        project.skills.remove(skill)
        return JsonResponse({"status": "ok"})
