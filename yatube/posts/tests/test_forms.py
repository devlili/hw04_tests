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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FormTest.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {"text": "Новый пост", "group": FormTest.group.pk}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": FormTest.user.username}
            ),
        )
        self.assertEqual(
            Post.objects.count(), posts_count + 1, "Запись не добавлена"
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {"text": "Редактированный пост"}
        self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": FormTest.post.pk},
            ),
            data=form_data,
        )
        self.assertTrue(
            Post.objects.filter(text="Редактированный пост").exists(),
            "Запись не редактируется",
        )
