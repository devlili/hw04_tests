from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class FormTest(TestCase):
    """Тестирование форм."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Pushkin")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый пост", author=cls.user, group=cls.group
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {"text": "Новый пост", "group": self.group.pk}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user.username}),
        )
        self.assertEqual(
            Post.objects.count(), posts_count + 1, "Запись не добавлена"
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, "Страница недоступна"
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {"text": "Редактированный пост"}
        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(text="Редактированный пост").exists(),
            "Запись не редактируется",
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, "Страница недоступна"
        )

    def test_guest_client_cant_create_edit_post(self):
        """Неавторизованный клиент не может создать/редактировать пост"""
        urls = (
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.pk},
            ),
            reverse("posts:post_create"),
        )
        login = reverse("users:login")
        for url in urls:
            with self.subTest(url=url):
                response = self.client.post(url, data={"text": "Чужой пост"})
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, f"{login}?next={url}")
