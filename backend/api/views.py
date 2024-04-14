from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import FoodgramUser, Subscription
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (
    FavoriteCreateSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeMinifiedSerializer,
    RecipeSerializer, ShoppingCartCreateSerializer,
    SubscriptionCreateSerializer, SubscriptionSerializer, TagSerializer,
)
from .utils import (generate_shopping_list_pdf, process_shopping_list)
from .permissions import IsAuthenticatedOrReadOnly
from .paginations import CustomPagination


class SubscriptionViewSet(viewsets.GenericViewSet):
    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self, request):
        return Subscription.objects.filter(
            user=request.user).order_by('-pk')

    @action(detail=False, methods=['get'], url_path='subscriptions',
            url_name='list_subscriptions')
    def list_subscriptions(self, request):
        page = self.paginate_queryset(self.get_queryset(request))
        serializer = SubscriptionSerializer(page,
                                            context={'request': request},
                                            many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            url_name='subscribe-unsubscribe')
    def subscribtion(self, request, **kwargs):
        author = get_object_or_404(FoodgramUser, id=kwargs['pk'])
        serializer = SubscriptionCreateSerializer(
            data={'author': author.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            subscription = serializer.save(user=request.user)
            return Response(SubscriptionSerializer(
                subscription,
                context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Subscription.objects.get(
                user=request.user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        query = self.request.query_params.get('name', '')
        queryset = Ingredient.objects.filter(name__istartwith=query)
        return queryset

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        )

        author_id = self.request.query_params.get('author', None)
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)

        tags = self.request.query_params.getlist('tags', [])
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        is_favorited = self.request.query_params.get('is_favorited', None)
        if is_favorited is not None:
            favorited_recipes_ids = self.request.user.favorites_user.all(
            ).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=favorited_recipes_ids)\
                if int(is_favorited)\
                else queryset.exclude(id__in=favorited_recipes_ids)

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None)
        if is_in_shopping_cart is not None:
            shopping_cart_recipe_ids = self.request.user.shopping_cart.all(
            ).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=shopping_cart_recipe_ids)\
                if int(is_in_shopping_cart)\
                else queryset.exclude(
                id__in=shopping_cart_recipe_ids)

        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    @staticmethod
    def common_action(serializer_class, model, pk, request):
        serializer = serializer_class(data={'recipe': pk,
                                            'user': request.user},
                                      context={'request': request})
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            obj = serializer.save(user=request.user)
            data = RecipeMinifiedSerializer(obj.recipe,
                                            context={'request': request}).data
            return Response(data=data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = model.objects.get(
                user=request.user,
                recipe=serializer.validated_data['recipe'])
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            url_name='action_with_favorits',
            permission_classes=[IsAuthenticated])
    def action_with_favorits(self, request, pk=None):
        return self.common_action(FavoriteCreateSerializer, Favorite,
                                  pk, request)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart',
            url_name='shopping_cart_actions',
            permission_classes=[IsAuthenticated])
    def shopping_cart_actions(self, request, pk=None):
        return self.common_action(ShoppingCartCreateSerializer, ShoppingCart,
                                  pk, request)

    @action(detail=True, methods=['get'], url_path='shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request, file_ext='pdf'):
        user = request.user
        current_user_shopping_list = Recipe.objects.filter(
            shoppingcart__user=user)
        shopping_list_items = process_shopping_list(current_user_shopping_list)

        if file_ext == 'pdf':
            content_type = 'application/pdf'
            buffer = generate_shopping_list_pdf(shopping_list_items, user)
        else:
            return Response(
                {'detail': 'Недопустимый формат файла.'},
                status=status.HTTP_400_BAD_REQUEST)

        response = FileResponse(buffer, content_type=content_type)
        filename = f'{user.username}_shopping_cart.{file_ext}'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
