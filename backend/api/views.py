import hashlib

from django.db.models import Sum
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            Favorites, ShoppingList, ShortLinkRecipe)
from api.serializers import (TagSerializer, RecipeSerializer,
                             IngredientSerializer, FavoriteSerializer,
                             ShoppingListSerializer)
from api.pagination import CustomPagination
from api.permissions import (IsAuthorOrReadOnlyPermissions,
                             IsAdminOrReadOnlyPermissions)
from api.filters import RecipeFilter, IngredientFilter
from core.views import create_shop_cart

ERROR_DICT = {
    'Favorites_post': {'Error': 'Рецепт уже в избранном!'},
    'Shopping_list_post': {'Error': 'Рецепт уже в списке покупок!'},
    'Favorites_delete': {'Error': 'Рецепта нет в избранном!'},
    'Shopping_list_delete': {'Error': 'Рецепта нет в списке покупок!'},
}


def create_delete_shop_favorites_or_shopping_cart(
        request, pk, model, class_serializer):
    """
    Вспомогательная функция для создания и удаления рецептов.
    Вызывается в методах RecipeViewSet.
    Параметры функции:
    1) request - объект запроса, хранящий данные запроса;
    2) pk - id рецепта из url запроса;
    3) model - модель, в данной функции FavoFavorites или ShoppingList;
    4) class_serializer - кастомные сериализаторы.
    """
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        if model.objects.filter(user=user, recipe=recipe).exists():
            if model.__name__ == 'Favorites':
                return Response(
                    ERROR_DICT['Favorites_post'],
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                ERROR_DICT['Shopping_list_post'],
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = class_serializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        serializer.is_valid()
        user = serializer.validated_data.get('user')
        recipe = serializer.validated_data.get('recipe')
        model.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    favorite_or_shop_list = model.objects.filter(user=user, recipe=recipe)
    if not favorite_or_shop_list.exists():
        if model.__name__ == 'Favorites':
            return Response(
                ERROR_DICT['Favorites_delete'],
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            ERROR_DICT['Shopping_list_delete'],
            status=status.HTTP_400_BAD_REQUEST
        )
    favorite_or_shop_list.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnlyPermissions,)
    pagination_class = None
    http_method_names = ['get', ]


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnlyPermissions,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None
    http_method_names = ['get', ]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermissions,)
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    @action(
        ['get', ], detail=True, url_path='get-link',
        permission_classes=[AllowAny, ]
    )
    def get_short_link(self, request, pk=None):
        """Метод для формирования и получения короткой ссылки."""
        original_link = self.request.build_absolute_uri()
        list_link = original_link.split('/')
        list_link.pop(-2)
        recipe_link = "/".join(list_link)
        recipe = get_object_or_404(Recipe, pk=pk)
        hash_value = hashlib.md5(recipe_link.encode()).hexdigest()[:3]
        ShortLinkRecipe.objects.get_or_create(
            recipe=recipe,
            defaults={'short_link': hash_value, 'original_link': recipe_link}
        )
        return Response({
            'short-link': self.request.build_absolute_uri(
                f'/s/{hash_value}'
            )},
            status=status.HTTP_200_OK
        )

    @action(
        ['post', 'delete', ], detail=True, url_path='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def add_or_delete_in_favorites(self, request, pk=None):
        """Метод, который добавляет либо удаляет рецепты из избранного."""
        return create_delete_shop_favorites_or_shopping_cart(
            request, pk, Favorites, FavoriteSerializer)

    @action(
        ['post', 'delete', ], detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def add_or_delete_recipes_shopping_cart(self, request, pk=None):
        """Метод, который добавляет либо удаляет рецепты из списка покупок."""
        return create_delete_shop_favorites_or_shopping_cart(
            request, pk, ShoppingList, ShoppingListSerializer)

    @action(
        ['get', ], detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def get_shopping_cart(self, request):
        """Метод для получения и скачивания списка покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppinglist__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_sum=Sum('amount'))
        shopping_list = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_sum']
            shopping_list.append(f'{name}   {amount}  ({measurement_unit})')

        response = create_shop_cart(shopping_list)
        response['Content-Disposition'] = 'attachment;' \
                                          'filename="shopping_list.pdf"'
        return response
