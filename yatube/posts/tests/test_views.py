from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

TEST_POSTS = 13
POSTS_1_PAGE = 10
POSTS_2_PAGE = 3


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
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(ViewsTest.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        reverse_templates_names = {
            reverse("posts:index"): "posts/index.html",
            (
                reverse(
                    "posts:group_list", kwargs={"slug": ViewsTest.group.slug}
                )
            ): "posts/group_list.html",
            (
                reverse(
                    "posts:profile",
                    kwargs={"username": ViewsTest.user.username},
                )
            ): "posts/profile.html",
            (
                reverse(
                    "posts:post_detail",
                    kwargs={"post_id": ViewsTest.post.pk},
                )
            ): "posts/post_detail.html",
            (
                reverse(
                    "posts:post_edit",
                    kwargs={"post_id": ViewsTest.post.pk},
                )
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in reverse_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f"{reverse_name} не соответсвует шаблону {template}",
                )

    def test_pages_show_correct_context(self):
        """Шаблоны index, group_list, profile сформированы
        с правильным контекстом."""
        reverses = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": ViewsTest.group.slug}),
            reverse(
                "posts:profile",
                kwargs={"username": ViewsTest.user.username},
            ),
        )
        for reverse_name in reverses:
            response = self.authorized_client.get(reverse_name)
            context = response.context["page_obj"][0]
            global contexts
            contexts = {
                context.text: ViewsTest.post.text,
                context.author: ViewsTest.post.author,
                context.group: ViewsTest.post.group,
            }
            for context, expected in contexts.items():
                with self.subTest(context=context):
                    self.assertEqual(
                        context,
                        expected,
                        "Шаблоны index, group_list, profile сформированы с"
                        " неправильным контекстом",
                    )

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": ViewsTest.post.pk},
            )
        )
        context = response.context["post"]
        for context, expected in contexts.items():
            self.assertEqual(
                context,
                expected,
                "Шаблон post_detail сформирован с неправильным контекстом",
            )

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = [
            ("text", forms.fields.CharField),
            ("group", forms.fields.ChoiceField),
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
            reverse(
                "posts:group_list", kwargs={"slug": f"{ViewsTest.group.slug}"}
            )
        )
        response_group_2 = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": f"{group_2.slug}"})
        )
        response_profile = self.authorized_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": f"{ViewsTest.user.username}"},
            )
        )
        index = response_index.context["page_obj"]
        group = response_group.context["page_obj"]
        another_group = response_group_2.context["page_obj"]
        profile = response_profile.context["page_obj"]
        self.assertIn(ViewsTest.post, index, "Поста нет на главной странице")
        self.assertIn(
            ViewsTest.post, group, "Поста нет на странице выбранной группы"
        )
        self.assertIn(
            ViewsTest.post, profile, "Поста нет в профайле пользователя"
        )
        self.assertNotIn(
            ViewsTest.post, another_group, "Пост попал в другую группу"
        )


class PaginatorViewsTest(TestCase):
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
        for post in range(TEST_POSTS):
            posts.append(
                Post(
                    text=f"Тестовый текст {post}",
                    group=cls.group,
                    author=cls.user,
                )
            )
        Post.objects.bulk_create(posts)
        cls.client = Client()

    def test_correct_page_context(self):
        """Тестирование паджинатора."""

        pages = [
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": PaginatorViewsTest.user.username},
            ),
            reverse(
                "posts:group_list",
                kwargs={"slug": PaginatorViewsTest.group.slug},
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
                POSTS_1_PAGE,
                error_name,
            )
            self.assertEqual(
                count_posts2,
                POSTS_2_PAGE,
                error_name,
            )
