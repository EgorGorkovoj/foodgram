from django_filters.rest_framework import filters, FilterSet

from api.models import Ingredient, Recipe, Tag
from users.models import CustomUser


class RecipeFilter(FilterSet):
    """Фильтрация рецептов."""

    author = filters.ModelMultipleChoiceFilter(
        queryset=CustomUser.objects.all(),
        field_name='author__username',
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='check_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='check_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags',
            'is_favorited', 'is_in_shopping_cart',
        )

    def check_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def check_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppinglist__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтрация ингредиентов."""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
