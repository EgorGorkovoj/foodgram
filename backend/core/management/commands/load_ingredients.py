import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from api.models import Ingredient


class Command(BaseCommand):
    """
    Класс для добавления ингредиентов в БД
    по команде 'python manage.py load_ingredients'.
    Ингредиенты беру из csv файла.
    """

    def handle(self, *args, **options):
        file_path = os.path.join(
            settings.BASE_DIR, 'data', 'ingredients.csv'
        )
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                Ingredient.objects.bulk_create(
                    Ingredient(name=line[0], measurement_unit=line[1])
                    for line in csv.reader(file)
                )
                self.stdout.write(
                    self.style.SUCCESS('Ингредиенты успешно добавлены!')
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR('Ингредиенты уже в базе!')
                )
