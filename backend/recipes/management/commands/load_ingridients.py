import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, **kwargs):
        file_path = './data/ingredients.csv'
        with open(
            file_path,
            'r',
            encoding='UTF-8'
        ) as file:
            reader = csv.reader(file, delimiter=',')

            ingredient_list = [
                Ingredient(
                    name=row[0],
                    measurement_unit=row[1]
                )
                for row in reader
            ]
        Ingredient.objects.bulk_create(ingredient_list)
        self.stdout.write(self.style.SUCCESS(
                          'Ингредиенты загружены'
                          ))
