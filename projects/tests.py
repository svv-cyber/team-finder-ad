from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from projects.constants import (
    TEST_PROJECT_NAME,
    TEST_PROJECT_DESCRIPTION,
    TEST_PROJECT_NAME_P,
    TEST_PROJECT_NAME_PYTHON,
    TEST_PROJECT_NAME_DJANGO,
    TEST_SKILL_PYTHON,
    TEST_SKILL_DJANGO,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TEST_USER_NAME,
    TEST_USER_SURNAME,
    OWNER_EMAIL,
    OWNER_PASSWORD,
    OWNER_NAME,
    OWNER_SURNAME,
    OTHER_EMAIL,
    OTHER_PASSWORD,
    OTHER_NAME,
    OTHER_SURNAME,
    SKILL_FILTER_OWNER_EMAIL,
    SKILL_FILTER_OWNER_PASSWORD,
    SKILL_FILTER_OWNER_NAME,
    SKILL_FILTER_OWNER_SURNAME,
    AUTOCOMPLETE_QUERY,
)
from projects.models import Project, Skill
from users.models import User


class ProjectListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            name=TEST_USER_NAME,
            surname=TEST_USER_SURNAME,
        )
        cls.project = Project.objects.create(
            name=TEST_PROJECT_NAME,
            description=TEST_PROJECT_DESCRIPTION,
            owner=cls.user,
            status=Project.STATUS_OPEN,
        )

    def test_list_page_renders(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.project.name)

    def test_detail_page_renders(self):
        response = self.client.get(
            reverse("projects:detail", kwargs={"pk": self.project.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.project.name)

    def test_root_redirects_to_project_list(self):
        response = self.client.get(reverse("root"))
        self.assertRedirects(response, reverse("projects:list"))

    def test_anonymous_cannot_create_project(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("users:login"), response.url)


class ProjectActionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email=OWNER_EMAIL,
            password=OWNER_PASSWORD,
            name=OWNER_NAME,
            surname=OWNER_SURNAME,
        )
        cls.other = User.objects.create_user(
            email=OTHER_EMAIL,
            password=OTHER_PASSWORD,
            name=OTHER_NAME,
            surname=OTHER_SURNAME,
        )
        cls.project = Project.objects.create(
            name=TEST_PROJECT_NAME_P,
            owner=cls.owner,
            status=Project.STATUS_OPEN,
        )

        cls.owner_client = Client()
        cls.owner_client.force_login(cls.owner)

        cls.other_client = Client()
        cls.other_client.force_login(cls.other)

    def test_owner_can_complete_project(self):
        response = self.owner_client.post(
            reverse("projects:complete", kwargs={"pk": self.project.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_other_user_cannot_complete_project(self):
        response = self.other_client.post(
            reverse("projects:complete", kwargs={"pk": self.project.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_user_can_join_and_leave_project(self):
        url = reverse(
            "projects:toggle_participate", kwargs={"pk": self.project.pk}
        )
        response = self.other_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.project.participants.filter(pk=self.other.pk).exists())

        response = self.other_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(self.project.participants.filter(pk=self.other.pk).exists())


class SkillFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email=SKILL_FILTER_OWNER_EMAIL,
            password=SKILL_FILTER_OWNER_PASSWORD,
            name=SKILL_FILTER_OWNER_NAME,
            surname=SKILL_FILTER_OWNER_SURNAME,
        )
        cls.python = Skill.objects.create(name=TEST_SKILL_PYTHON)
        cls.django = Skill.objects.create(name=TEST_SKILL_DJANGO)
        cls.python_project = Project.objects.create(
            name=TEST_PROJECT_NAME_PYTHON, owner=cls.owner, status=Project.STATUS_OPEN
        )
        cls.python_project.skills.add(cls.python)
        cls.django_project = Project.objects.create(
            name=TEST_PROJECT_NAME_DJANGO, owner=cls.owner, status=Project.STATUS_OPEN
        )
        cls.django_project.skills.add(cls.django)

    def test_filter_by_skill_keeps_matching_projects(self):
        response = self.client.get(reverse("projects:list"), {"skill": TEST_SKILL_PYTHON})
        self.assertContains(response, TEST_PROJECT_NAME_PYTHON)
        self.assertNotContains(response, TEST_PROJECT_NAME_DJANGO)

    def test_skill_autocomplete_returns_matches(self):
        response = self.client.get(
            reverse("projects:skills_autocomplete"), {"q": AUTOCOMPLETE_QUERY}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        names = [item["name"] for item in data]
        self.assertIn(TEST_SKILL_PYTHON, names)