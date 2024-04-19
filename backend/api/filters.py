from django_filters import rest_framework
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient


class IngredientFilter(FilterSet):

    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
