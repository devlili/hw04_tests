from django.core.paginator import Paginator

from yatube.settings import POSTS_PER_PAGE


def paginate(request, posts):
    """Паджинатор - разбивка на страницы."""
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
