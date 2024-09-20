from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.models import (Tag, Ingredient, Recipe,
                        Favorites, ShoppingList)
from api.serializers import (TagSerializer, RecipeSerializer,
                             IngredientSerializer, FavoriteSerializer,
                             ShoppingListSerializer)
from api.permissions import (IsAuthorOrReadOnlyPermissions,
                             IsAdminOrReadOnlyPermissions)                    


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


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Favorite."""
    queryset = Favorites.objects.all()
    serializer_class = FavoriteSerializer
    # permission_classes = ...  # Авторизация по токену.
    pagination_class = ...
    http_method_names = ['post', 'delete',]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermissions,)  # Авторизация по токену.
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete',]
    filterset_fields = (
        'is_favorited', 'is_in_shopping_cart',
        'author', 'tags',
    )
