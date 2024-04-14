from django_filters import rest_framework
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):

    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:

        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):

    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())

    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    def is_favorited_filter(self, queryset, request, value):
        if value:
            favorited_recipes_ids = (
                self.request.user.user_favorits.values_list('recipe_id',
                                                            flat=True))
            queryset = queryset.filter(id__in=favorited_recipes_ids)
            return queryset
        return queryset

    def is_in_shopping_cart_filter(self, queryset, request, value):
        if value:
            shopping_cart_recipe_ids = self.request.user.shopping_cart.all(
            ).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=shopping_cart_recipe_ids)
            return queryset
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
