from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Recipe, ShoppingCart, Tag, Ingredient
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import FoodgramUser, Subscription

from .serializers import (
    FavoriteCreateSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeMinifiedSerializer, RecipeSerializer, ShoppingCartCreateSerializer,
    SubscriptionCreateSerializer, SubscriptionSerializer, TagSerializer)
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .utils import generate_shopping_list_pdf, process_shopping_list
from api.paginations import CustomPagination


class SubscriptionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', 'delete')

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        queryset = FoodgramUser.objects.filter(subscribers__user=request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionSerializer(page, many=True,
                                            context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(FoodgramUser, id=kwargs['pk'])
        serializer = SubscriptionCreateSerializer(
            data={'author': author.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            subscription = serializer.save(user=request.user)
            serialized_data = SubscriptionSerializer(
                author, context={'request': request}).data
            return Response(serialized_data, status=status.HTTP_201_CREATED)

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
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    http_method_names = ['get']
    lookup_field = 'id'
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

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

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
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
