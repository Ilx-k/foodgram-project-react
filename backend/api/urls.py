from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet, RecipeViewSet,
    SubscriptionViewSet, TagViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()
router.register('subscriptions', SubscriptionViewSet,
                basename='subscriptions')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)), ]
