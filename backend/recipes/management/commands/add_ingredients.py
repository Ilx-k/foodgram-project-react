import csv

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILES_DIR
from recipes.models import Ingredient


def import_data():
    try:
        with open(f'{CSV_FILES_DIR}/ingredients.csv',
                  encoding='utf-8') as csvfile:
            fieldnames = ['name', 'measurement_unit']
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            for row in reader:
                Ingredient.objects.create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'])
    except FileNotFoundError:
        print("Файл не найден.")
    except UnicodeDecodeError:
        print("Не удается расшифровать файл в указанной кодировке.")


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **options):
        import_data()
        self.stdout.write(self.style.SUCCESS(
            f'В базу данных загружено '
            f'{Ingredient.objects.count()} ингредиентов'))
