import re

from django.core.exceptions import ValidationError

from .constants import (SCORE_MIN, AMOUNT_SCORE_MAX, SCORE_MAX)


def validate_name(value):
    if re.search(r'^[а-яА-ЯёЁa-zA-Z]+$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в имени или фамилии.'),
            params={'value': value},
        )
    return value


def validate_recipe_name(value):
    if re.search(r'^[а-яА-ЯёЁa-zA-Z0-9_\-\.\(\)\s]+$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в имени или фамилии.'),
            params={'value': value},
        )
    return value


def validate_hex_color(value):
    if re.search(r'^#([A-Fa-f0-9]{3,6})$', value) is None:
        raise ValidationError(
            ('Не соответствует формату цвета HEX.'),
            params={'value': value},
        )
    return value


def validate_amount(value):
    if int(value) < SCORE_MIN:
        raise ValidationError(f'Количество не '
                              f'должно быть меньше {SCORE_MIN}.')
    if int(value) > AMOUNT_SCORE_MAX:
        raise ValidationError(f'Количество не должно '
                              f'быть больше {AMOUNT_SCORE_MAX}.')
    return value


def validate_cooking_time(value):
    if int(value) < SCORE_MIN:
        raise ValidationError(
            'Время готовки не должно быть меньше минуты')
    if int(value) > SCORE_MAX:
        raise ValidationError(
            'Время готовки не должно быть больше суток')
    return value
