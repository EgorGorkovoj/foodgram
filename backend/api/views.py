import os
import pdb
import hashlib

from django.conf import settings
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotFound, HttpResponse, FileResponse

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                        Favorites, ShoppingList, ShortLinkRecipe)
from api.serializers import (TagSerializer, RecipeSerializer,
                             IngredientSerializer, FavoriteSerializer,
                             ShoppingListSerializer)
from api.pagination import CustomPagination
from api.permissions import (IsAuthorOrReadOnlyPermissions,
                             IsAdminOrReadOnlyPermissions)              

import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader


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


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermissions,)
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
    def add_or_delete_in_favorites(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorites.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'Error': 'Рецепт уже в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FavoriteSerializer(
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

    @action(
        ['post', 'delete', ], detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def add_or_delete_recipes_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'Error': 'Рецепт уже в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = ShoppingListSerializer(
                data={'user': user.id, 'recipe': recipe.id}
            )
            serializer.is_valid()
            user = serializer.validated_data.get('user')
            recipe = serializer.validated_data.get('recipe')
            ShoppingList.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shop_list = ShoppingList.objects.filter(
            user=user, recipe=recipe
        )
        if not shop_list.exists():
            return Response(
                {'Error': 'Рецепта нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shop_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get', ], detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def get_shopping_cart(self, request):
        # pdb.set_trace()
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

        # Регистрируем шрифт для отображения киррилицы.
        pdfmetrics.registerFont(TTFont('Gabriola', 'gabriola.ttf'))
        pdfmetrics.registerFont(TTFont('Georgia', 'georgia.ttf'))
        # Открываем файл с фоном.
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        # Путь до картинки.
        img_path = os.path.join(
            settings.BASE_DIR, 'api', 'templates', 'Shopp_list.jpg'
        )
        # Делаю фон.
        background = ImageReader(img_path)
        can.drawImage(background, 0, 0, width=letter[0], height=letter[1])
        title = 'Cписок покупок: '
        # Шрифт.
        can.setFont('Georgia', 18)
        y_title = (letter[1] - 0.5 * inch) - 4.3 * cm
        x_title = (letter[0] - can.stringWidth(
            " ".join(title), 'Georgia', 22)) - 4.2 * cm
        can.drawString(x_title, y_title, title)
        can.setFont('Gabriola', 18)
        y = (letter[1] - 0.5 * inch) - 5 * cm
        x = (letter[0] - can.stringWidth(
            " ".join(shopping_list), 'Gabriola', 18)) - 2.5 * cm
        # Отображаем список покупок.
        for item in shopping_list:
            can.drawString(x, y, item)
            y -= 0.2 * inch

        can.save()
        packet.seek(0)

        response = HttpResponse(packet.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment;' \
                                          'filename="shopping_list.pdf"'
        return response
