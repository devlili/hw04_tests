from django.test import TestCase

from ..models import Group, Post, User


class ModelTest(TestCase):
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
            author=cls.user,
            text="Тестовый пост",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        group = ModelTest.group
        post = ModelTest.post
        expected_object_name = {
            group.title: str(group),
            post.text: str(post),
        }
        for value, expected in expected_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                    f"У модели {value} некорректно работает __str__",
                )
