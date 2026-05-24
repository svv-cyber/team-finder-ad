"""Вспомогательные функции уровня приложения users."""

from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page", 1)
    return paginator.get_page(page_number)