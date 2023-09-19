from django_filters import rest_framework as filters

from foodgram.models import Recipe


class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter(
        field_name='author',
    )
    tags = filters.CharFilter(
        field_name='tags__slug',
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user

        return (queryset.filter(favorited__user=user) if value is True
                else queryset.exclude(favorited__user=user) if value is False
                else queryset)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user

        return (queryset.filter(shopping_carts__user=user) if value is True
                else queryset.exclude(
                    shopping_carts__user=user) if value is False
                else queryset)
