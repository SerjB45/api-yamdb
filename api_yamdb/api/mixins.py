from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from .permissions import IsAdminOrReadOnly


class CommonSettingMixin:
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)


class GenreCategoryMixin:
    http_method_names = ('get', 'post', 'delete',)
    search_fields = ('name',)
    lookup_field = 'slug'
