import io
import os

from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

from recipes.models import ShortLinkRecipe

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader


def redirect_original_url(request, short_link):
    """
    Функция для получения рецепта из короткой ссылки.
    Параметры функции:
    1) short_link - набор зашифрованных символов,
       который приходит из запроса <str:short_link>.
    """
    try:
        url = ShortLinkRecipe.objects.get(short_link=short_link)
        original_link = url.original_link
        list_link = original_link.split('/')
        list_link.pop(-4)
        recipe_link = "/".join(list_link)
        return redirect(recipe_link)
    except ShortLinkRecipe.DoesNotExist:
        return HttpResponseNotFound("Короткая ссылка не найдена!")


def create_shop_cart(shopping_list):
    """
    Вспомогательная функция для формирования списка покупок
    в виде pfd файла.
    Вызывается в методe get_shopping_cart RecipeViewSet.
    Параметры функции:
    1) shopping_list - сформированный и отфильтрованный список
       ингредиентов с их количеством.
    """
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
    y_ingredient = (letter[1] - 0.5 * inch) - 4.8 * cm
    # Отображаем список покупок.
    for item in shopping_list:
        x_ingredient = (letter[0] - can.stringWidth(
            f' {item} ', 'Gabriola', 18)) - 8.5 * cm
        can.drawString(x_ingredient, y_ingredient, item)
        y_ingredient -= 0.2 * inch
    can.save()
    packet.seek(0)
    return HttpResponse(packet.read(), content_type='application/pdf')
