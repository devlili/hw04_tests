from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для групп."""
    title = models.CharField("Название группы", max_length=200)
    description = models.TextField("Описание группы")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Адрес для страницы с группой",
        help_text=(
            "Укажите адрес для страницы группы. Используйте только "
            "латиницу, цифры, дефисы и знаки подчёркивания"
        ),
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель для постов."""
    text = models.TextField("Текст поста", help_text="Введите текст поста")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ("-pub_date", "-id")

    def __str__(self):
        return self.text[:15]
