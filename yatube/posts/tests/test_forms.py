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
        old_text = self.post
        group2 = Group.objects.create(title="Тестовая группа2", slug="slug-2")
        form_data = {"text": "Редактированный пост", "group": group2.id}
        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(
                text="Редактированный пост", group=group2.id
            ).exists(),
            "Запись не редактируется",
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, "Страница недоступна"
        )
        self.assertNotEqual(
            old_text.text,
            form_data["text"],
            "Пользователь не может изменить содержание поста",
        )
        self.assertNotEqual(
            old_text.group,
            form_data["group"],
            "Пользователь не может изменить группу поста",
        )

    def test_group_null(self):
        """Проверка, что группу можно не указывать"""
        old_text = self.post
        form_data = {"text": "Редактированный пост", "group": ""}
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(
            old_text.group,
            form_data["group"],
            "Пользователь не может оставить группу пустым",
        )

    def test_guest_client_cant_create_edit_post(self):
        """Неавторизованный клиент не может создать/редактировать пост"""
        posts_count = Post.objects.count()
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
                self.assertNotEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    "Неавторизованный пользователь может создать/"
                    " редактировать пост",
                )
                self.assertRedirects(response, f"{login}?next={url}")
                self.assertNotEqual(
                    Post.objects.count(),
                    posts_count + 1,
                    "Пост добавлен по ошибке неавторизованным пользователем",
                )
