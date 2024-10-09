import io
import os

from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

from api.models import Recipe, ShortLinkRecipe

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader


ERROR_DICT = {
    'Favorites_post': {'Error': 'Рецепт уже в избранном!'},
    'Shopping_list_post': {'Error': 'Рецепт уже в списке покупок!'},
    'Favorites_delete': {'Error': 'Рецепта нет в избранном!'},
    'Shopping_list_delete': {'Error': 'Рецепта нет в списке покупок!'},
}
STATUS_RESPONSE = {
    '400': status.HTTP_400_BAD_REQUEST,
    '204': status.HTTP_204_NO_CONTENT,
    '201': status.HTTP_201_CREATED
}


def redirect_original_url(request, short_link):
    """Функция для получения рецепта из короткой ссылки."""
    try:
        url = ShortLinkRecipe.objects.get(short_link=short_link)
        url.save()
        return redirect(url.original_link)
    except ShortLinkRecipe.DoesNotExist:
        return HttpResponseNotFound("Короткая ссылка не найдена!")


def create_delete_shop_favorites_or_shopping_cart(
        request, pk, model, class_serializer):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        if model.objects.filter(user=user, recipe=recipe).exists():
            if model.__name__ == 'Favorites':
                return Response(
                    ERROR_DICT['Favorites_post'],
                    status=STATUS_RESPONSE['400']
                )
            return Response(
                ERROR_DICT['Shopping_list_post'],
                status=STATUS_RESPONSE['400']
            )
        serializer = class_serializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        serializer.is_valid()
        user = serializer.validated_data.get('user')
        recipe = serializer.validated_data.get('recipe')
        model.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=STATUS_RESPONSE['201'])
    favorite_or_shop_list = model.objects.filter(user=user, recipe=recipe)
    if not favorite_or_shop_list.exists():
        if model.__name__ == 'Favorites':
            return Response(
                ERROR_DICT['Favorites_delete'],
                status=STATUS_RESPONSE['400']
            )
        return Response(
            ERROR_DICT['Shopping_list_delete'],
            status=STATUS_RESPONSE['400']
        )
    favorite_or_shop_list.delete()
    return Response(status=STATUS_RESPONSE['204'])


def create_shop_cart(shopping_list):
    gabriola_path = os.path.join(
        settings.BASE_DIR, 'api', 'templates', 'gabriola.ttf'
    )
    georgia_path = os.path.join(
        settings.BASE_DIR, 'api', 'templates', 'georgia.ttf'
    )

    # Регистрируем шрифт для отображения киррилицы.
    pdfmetrics.registerFont(
        TTFont('Gabriola', gabriola_path)
    )
    pdfmetrics.registerFont(TTFont(
        'Georgia', georgia_path)
    )
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
    can.setFont('Gabriola', 16)
    y = (letter[1] - 0.5 * inch) - 4.8 * cm
    x = (letter[0] - can.stringWidth(
        " ".join(shopping_list), 'Gabriola', 18)) - 5 * cm
    # Отображаем список покупок.
    for item in shopping_list:
        can.drawString(x, y, item)
        y -= 0.2 * inch
    can.save()
    packet.seek(0)
    return HttpResponse(packet.read(), content_type='application/pdf')
