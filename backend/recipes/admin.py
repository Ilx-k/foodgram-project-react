from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag)
from .constants import SCORE_MIN, AMOUNT_SCORE_MAX


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = SCORE_MIN
    max_num = AMOUNT_SCORE_MAX
    validate_min = True
    validate_max = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'pk',
        'pub_date',
        'name',
        'author',
        'text',
        'image',
        'get_count_in_favourite'
    )
    list_display_links = ('name',)
    search_fields = (
        'name',
        'author',
        'text',
        'ingredients'
    )
    list_editable = (
        'author',
    )
    list_filter = ('tags',)
    empty_value_display = '-пусто-'

    @admin.display(description='Количество в избранных')
    def get_count_in_favourite(self, object):
        return object.favorites_user.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_filter = ('measurement_unit',)
    list = (
        'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    list_editable = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    list_editable = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'
