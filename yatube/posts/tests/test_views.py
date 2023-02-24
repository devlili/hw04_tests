import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import POSTS_PER_PAGE

from ..models import Group, Post, User

GAP = 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTest(TestCase):
    """Тестирование Views."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Pushkin")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            image=uploaded,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_show_correct_context(self):
        """Шаблоны index, group_list, profile сформированы
        с правильным контекстом.
        """
        reverses = (
            reverse("posts:index"),
            reverse("posts:group_list", args=(self.group.slug,)),
            reverse(
                "posts:profile",
                args=(self.user.username,),
            ),
        )
        for reverse_name in reverses:
            response = self.authorized_client.get(reverse_name)
            context = response.context["page_obj"][0]
            contexts = {
                context.text: self.post.text,
                context.author: self.post.author,
                context.group: self.post.group,
                context.image: self.post.image,
            }
            for value, expected in contexts.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        value,
                        expected,
                        "Шаблоны index, group_list, profile сформированы с"
                        " неправильным контекстом",
                    )

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_detail",
                args=(self.post.pk,),
            )
        )
        context = response.context["post"]
        contexts = {
            context.text: self.post.text,
            context.author: self.post.author,
            context.group: self.post.group,
            context.image: self.post.image,
        }
        for value, expected in contexts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                    "Шаблон post_detail сформирован с неправильным контекстом",
                )

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = [
            ("text", forms.fields.CharField),
            ("group", forms.fields.ChoiceField),
            ("image", forms.fields.ImageField),
        ]
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    "Шаблон create_post сформирован с неправильным контекстом",
                )

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        group_2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="test-slug2",
            description="Тестовое описание",
        )
        response_index = self.authorized_client.get(reverse("posts:index"))
        response_group = self.authorized_client.get(
            reverse("posts:group_list", args=(self.group.slug,))
        )
        response_group_2 = self.authorized_client.get(
            reverse("posts:group_list", args=(group_2.slug,))
        )
        response_profile = self.authorized_client.get(
            reverse(
                "posts:profile",
                args=(self.user.username,),
            )
        )
        index = response_index.context["page_obj"]
        group = response_group.context["page_obj"]
        another_group = response_group_2.context["page_obj"]
        profile = response_profile.context["page_obj"]
        self.assertIn(self.post, index, "Поста нет на главной странице")
        self.assertIn(
            self.post, group, "Поста нет на странице выбранной группы"
        )
        self.assertIn(self.post, profile, "Поста нет в профайле пользователя")
        self.assertNotIn(
            self.post, another_group, "Пост попал в другую группу"
        )


class Paginatorself(TestCase):
    """Тестирование паджинатора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Pushkin")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        posts = []
        for post in range(POSTS_PER_PAGE + GAP):
            posts.append(
                Post(
                    text=f"Тестовый текст {post}",
                    group=cls.group,
                    author=cls.user,
                )
            )
        Post.objects.bulk_create(posts)

    def test_correct_page_context(self):
        """Тестирование паджинатора."""

        cache.clear()
        pages = [
            reverse("posts:index"),
            reverse(
                "posts:profile",
                args=(self.user.username,),
            ),
            reverse(
                "posts:group_list",
                args=(self.group.slug,),
            ),
        ]
        for page in pages:
            response1 = self.client.get(page)
            response2 = self.client.get(page + "?page=2")
            count_posts1 = len(response1.context["page_obj"])
            count_posts2 = len(response2.context["page_obj"])
            error_name = "Неверное отображение количества постов на странице"
            self.assertEqual(
                count_posts1,
                POSTS_PER_PAGE,
                error_name,
            )
            self.assertEqual(
                count_posts2,
                GAP,
                error_name,
            )
