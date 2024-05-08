from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import FoodgramUser
from .validators import (
    validate_name, validate_hex_color, validate_recipe_name,
    validate_cooking_time, validate_amount)
from .constants import CHAR_LENGTH, TEXT_LENGTH, COLOR_LENGTH


class Tag(models.Model):
    name = models.CharField(
        verbose_name=_('Название тега'),
        validators=(validate_name,),
        max_length=CHAR_LENGTH,
        unique=True
    )
    color = models.CharField(
        verbose_name=_('HEX-цвет тега'),
        validators=(validate_hex_color,),
        max_length=COLOR_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=CHAR_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_('Название ингредиента'),
        validators=(validate_name,),
        max_length=CHAR_LENGTH,
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name=_('Единица измерения'),
        max_length=CHAR_LENGTH,
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Список тегов'),
        help_text='Выставите теги',
    )
    author = models.ForeignKey(
        get_user_model(),
        verbose_name=_('Автор рецепта'),
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name=_('Название'),
        validators=(validate_recipe_name,),
        max_length=CHAR_LENGTH,
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name=_('Ссылка на картинку на сайте'),
        upload_to='rescipes/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )
    text = models.CharField(
        verbose_name=_('Описание'),
        max_length=TEXT_LENGTH,
        help_text='Составьте описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('Время приготовления (в минутах)'),
        validators=(validate_cooking_time,),
        help_text='Введите время готовки (мин.)'
    )
    pub_date = models.DateTimeField(
        verbose_name=_('Дата публикации'),
        auto_now_add=True,
        db_index=True,
        editable=False
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('Рецепт'),
        related_name='ingredientes',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ингредиент'),
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name=_('Количество'),
        validators=(validate_amount,),
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('id',)
        unique_together = ('recipe', 'ingredient')


class Favorite(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name=_('Пользователь'),
        help_text='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        help_text='Рецепт',
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранные')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} >> {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Пользователь'),
        help_text='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        help_text='Рецепт',
    )

    class Meta:
        verbose_name = _('Корзина покупок')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} >> {self.recipe}'
