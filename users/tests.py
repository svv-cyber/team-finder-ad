from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from users.constants import (
    EXISTING_USER_EMAIL,
    EXISTING_USER_PASSWORD,
    EXISTING_USER_NAME,
    EXISTING_USER_SURNAME,
    TEST_NAME,
    TEST_SURNAME,
    TEST_EMAIL,
    TEST_PASSWORD,
    OWNER_EMAIL,
    OWNER_PASSWORD,
    OWNER_NAME,
    OWNER_SURNAME,
    INVALID_EMAIL,
    INVALID_PASSWORD,
    ERROR_MESSAGE_INVALID,
)
from users.models import User


class UserAuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.existing_user = User.objects.create_user(
            email=EXISTING_USER_EMAIL,
            password=EXISTING_USER_PASSWORD,
            name=EXISTING_USER_NAME,
            surname=EXISTING_USER_SURNAME,
        )

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "name": TEST_NAME,
                "surname": TEST_SURNAME,
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
        )
        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email=TEST_EMAIL).exists())

    def test_login_with_valid_credentials_redirects_to_projects(self):
        response = self.client.post(
            reverse("users:login"),
            data={"email": EXISTING_USER_EMAIL, "password": EXISTING_USER_PASSWORD},
        )
        self.assertRedirects(response, reverse("projects:list"))

    def test_login_with_invalid_credentials_shows_error(self):
        response = self.client.post(
            reverse("users:login"),
            data={"email": INVALID_EMAIL, "password": INVALID_PASSWORD},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, ERROR_MESSAGE_INVALID)

    def test_participants_page_is_public(self):
        response = self.client.get(reverse("users:participants"))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class UserProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email=OWNER_EMAIL,
            password=OWNER_PASSWORD,
            name=OWNER_NAME,
            surname=OWNER_SURNAME,
        )

    def test_anonymous_can_view_profile(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"pk": self.user.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_cannot_edit_profile(self):
        response = self.client.get(reverse("users:edit_profile"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("users:login"), response.url)