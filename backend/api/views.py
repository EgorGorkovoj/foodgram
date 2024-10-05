import pdb
import hashlib

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotFound

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import (Tag, Ingredient, Recipe,
                        Favorites, ShoppingList, ShortLinkRecipe)
from api.serializers import (TagSerializer, RecipeSerializer,
                             IngredientSerializer, FavoriteSerializer,
                             ShoppingListSerializer)
from api.pagination import CustomPagination
from api.permissions import (IsAuthorOrReadOnlyPermissions,
                             IsAdminOrReadOnlyPermissions)              


def redirect_original_url(request, short_link):
    """Функция для получения рецепта из короткой ссылки."""
    try:
        short_url = request.build_absolute_uri(
            f'/s/{short_link}')
        url = ShortLinkRecipe.objects.get(short_link=short_url)
        url.save()
        return redirect(url.original_link)
    except ShortLinkRecipe.DoesNotExist:
        return HttpResponseNotFound("Короткая ссылка не надена!")


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnlyPermissions,)
    pagination_class = None
    http_method_names = ['get',]


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnlyPermissions,)
    pagination_class = None
    http_method_names = ['get',]


# class FavoriteViewSet(viewsets.ModelViewSet):
#     """Вьюсет модели Favorite."""
#     queryset = Favorites.objects.all()
#     serializer_class = FavoriteSerializer
#     permission_classes = IsAuthenticated  # Авторизация по токену.
#     pagination_class = ...
#     http_method_names = ['post', 'delete',]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermissions,)  # Авторизация по токену.
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'patch', 'delete',]
    # filterset_fields = (
    #     'is_favorited', 'is_in_shopping_cart',
    #     'author', 'tags',
    # )

    @action(
        ['get', ], detail=True, url_path='get-link',
        permission_classes=[AllowAny, ]
    )
    def get_short_link(self, request, pk=None):
        # pdb.set_trace()
        original_link = self.request.build_absolute_uri()
        list_link = original_link.split('/')
        list_link.pop(-2)
        recipe_link = "/".join(list_link)
        recipe = get_object_or_404(Recipe, pk=pk)
        hash_value = hashlib.md5(recipe_link.encode()).hexdigest()[:3]
        short_url = self.request.build_absolute_uri(
            f'/s/{hash_value}'
        )
        ShortLinkRecipe.objects.get_or_create(
            recipe=recipe, short_link=short_url, original_link=recipe_link
        )
        return Response({'short-url': short_url}, status=status.HTTP_200_OK)

    @action(
        ['post', 'delete', ], detail=True, url_path='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def add_in_favorites(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                context={'request': request},
                data={'user': user.id, 'recipe': recipe.id}
            )
            serializer.is_valid()
            user = serializer.validated_data.get('user')
            recipe = serializer.validated_data.get('recipe')
            Favorites.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = Favorites.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'Error': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
