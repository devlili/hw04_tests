from core.utils import paginate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    """Главная страница."""
    template = "posts/index.html"
    title = "Последние обновления на сайте"
    posts = Post.objects.select_related("author", "group")
    page_obj = paginate(request, posts)
    context = {
        "title": title,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Страница постов одной группы."""
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества "{group}"'
    posts = group.posts.select_related("author", "group")
    page_obj = paginate(request, posts)
    context = {
        "title": title,
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Страница профайла пользователя."""
    template = "posts/profile.html"
    user = get_object_or_404(User, username=username)
    post_list = user.posts.select_related("author", "group")
    page_obj = paginate(request, post_list)
    context = {
        "page_obj": page_obj,
        "author": user,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница поста."""
    template = "posts/post_detail.html"
    user_post = get_object_or_404(Post, id=post_id)
    title = f"Пост {user_post}"
    context = {
        "title": title,
        "post": user_post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Страница добавления нового поста."""
    template = "posts/create_post.html"
    title = "Новый пост"
    button = "Добавить"
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=post.author)
    context = {
        "title": title,
        "button": button,
        "form": form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста."""
    template = "posts/create_post.html"
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)
    title = "Редактировать запись"
    button = "Сохранить"
    form = PostForm(request.POST or None, instance=post)
    context = {
        "form": form,
        "title": title,
        "button": button,
    }
    if not form.is_valid():
        return render(request, template, context)
    form.save()
    return redirect("posts:post_detail", post_id=post_id)
