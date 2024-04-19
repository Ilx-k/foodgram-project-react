from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
    SubscriptionViewSet, TagViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet,
                basename='subscriptions')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.authtoken')),
    path('tags/<int:pk>/', TagViewSet.as_view({'get': 'retrieve'}),
         name='tag-detail'),
    path('users/subscriptions/', SubscriptionViewSet.as_view(
        {'get': 'list_subscriptions'}), name='subscriptions-list'),
    path('users/<int:pk>/subscribe/',
         SubscriptionViewSet.as_view({'post': 'subscribe',
                                      'delete': 'subscribe'}),
         name='subscribe-unsubscribe'),
    path('recipes/<int:pk>/favorite/',
         RecipeViewSet.as_view({'post': 'add_favorite',
                                'delete': 'remove_favorite'}),
         name='add_favorite-remove_favorite'),
    path('recipes/<int:pk>/shopping_cart/',
         RecipeViewSet.as_view({'post': 'add_shopping_cart',
                                'delete': 'remove_shopping_cart'}),
         name='add_shopping_cart-remove_shopping_cart'),
    path('recipes/download_shopping_cart/', ShoppingCartViewSet.as_view(
        {'get': 'download_shopping_cart'}), name='download_shopping_cart'),
    path('', include(router.urls)), ]
