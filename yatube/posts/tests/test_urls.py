from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class URLTests(TestCase):
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

        global url_templates_names
        url_templates_names = {
            "/": "posts/index.html",
            f"/group/{cls.group.slug}/": "posts/group_list.html",
            f"/profile/{cls.user.username}/": "posts/profile.html",
            f"/posts/{cls.post.pk}/": "posts/post_detail.html",
            f"/posts/{cls.post.pk}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(URLTests.user)

    def test_url_exists_at_desired_location(self):
        """Общедоступные страницы."""
        for url in url_templates_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                global error_name
                error_name = f"Нет доступа к странице {url}"
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, error_name
                )

    def test_url_exists_for_authorized_client(self):
        """Страницы доступны авторизованным пользователям."""
        for url in url_templates_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, error_name
                )

    def test_url_exists_for_author(self):
        """Страница /posts/<post_id>/edit/ доступна только автору поста."""
        user = User.objects.create_user(username="Lermontov")
        authorized_client = Client()
        authorized_client.force_login(user)
        response = authorized_client.get(f"/posts/{URLTests.post.pk}/edit/")
        self.assertNotEqual(
            response.status_code,
            HTTPStatus.OK,
            "Чужак пытается отредактировать пост",
        )

    def test_url_redirect_anonymous_on_auth_login(self):
        """Страницы для неавторизованного пользователя перенаправят анонимного
        пользователя на страницу логина.
        """
        url_names = (f"/posts/{URLTests.post.pk}/edit/", "/create/")
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f"/auth/login/?next={url}")

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    f"{address} не соответсвует шаблону {template}",
                )

    def test_unexisting_page(self):
        """Запрос к несуществующей странице."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            "Ошибка запроса к несуществующей странице",
        )
