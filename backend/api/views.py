from datetime import date

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from recipes.models import Favorite, Recipe, ShoppingCart, Tag, Ingredient
from users.models import CustomUser, Subscription
from .serializers import (
    CustomUserSerializer, CustomUserSignUpSerializer, FavoriteCreteSerializer,
    IngredientSerializer, RecipeCreateSerializer, RecipeMinifiedSerializer,
    RecipeSerializer, ShoppingCartCreateSerializer,
    SubscriptionCreateSerializer, SubscriptionSerializer, TagSerializer)
from .utils import generate_shopping_list_pdf, process_shopping_list
from .filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import AuthorOrReadOnly


class CustomUserViewSet(UserViewSet):

    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserSignUpSerializer
        return CustomUserSerializer

    def get_subscribed_recipes(self, user):
        subscribed_users = user.following.all()
        subscribed_recipes = Recipe.objects.filter(
            author__in=subscribed_users,
            pub_date__lte=date.today())
        return subscribed_recipes

    def paginate_and_serialize(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True,
                context={'request': self.request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True,
            context={'request': self.request})
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        is_subscribed = request.query_params.get('is_subscribed', False)

        if is_subscribed:
            user = request.user
            queryset = CustomUser.objects.prefetch_related(
                'recipes').filter(subscriptions__user=user)
        else:
            queryset = CustomUser.objects.prefetch_related('recipes')

        return self.paginate_and_serialize(queryset)

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']

            if self.request.user.check_password(current_password):
                self.request.user.set_password(new_password)
                self.request.user.save()
                return Response(status=204)
            else:
                return Response({'detail': 'Пароли не совпадают.'},
                                status=400)
        else:
            return Response(serializer.errors, status=400)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit = self.request.query_params.get('recipes_limit', None)

        if recipes_limit is not None:
            recipes_queryset = instance.recipes.all()[:recipes_limit]
        else:
            recipes_queryset = instance.recipes.all()

        representation['recipes'] = RecipeMinifiedSerializer(recipes_queryset,
                                                             many=True).data
        return representation

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_user(self, pk):
        return get_object_or_404(CustomUser, id=pk)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            url_name='list_subscriptions')
    def list_subscriptions(self, request):
        queryset = Subscription.objects.filter(
            user=request.user).order_by('-pk')
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_queryset,
                                         context={'request': request},
                                         many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subscribe',
            url_name='subscribe')
    def subscribe(self, request, pk=None):
        target_user = self.get_user(pk)
        serializer = SubscriptionCreateSerializer(
            data={'author': target_user.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save(user=request.user)
        return Response(SubscriptionSerializer(
            subscription,
            context={'request': request}).data,
            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='subscribe',
            url_name='unsubscribe')
    def unsubscribe(self, request, pk=None):
        target_user = self.get_user(pk)
        serializer = SubscriptionCreateSerializer(
            data={'author': target_user.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        subscription = Subscription.objects.get(
            user=request.user, author=target_user)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TagListView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter


    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        if self.action == 'update' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post'], url_path='favorite',
            url_name='add_favorite', permission_classes=[IsAuthenticated])
    def add_favorite(self, request, pk=None):
        serializer = FavoriteCreteSerializer(data={'recipe': pk},
                                             context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorite = serializer.save(user=request.user)
        favorite_data = RecipeMinifiedSerializer(
            favorite.recipe,
            context={'request': request}).data
        return Response(data=favorite_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='favorite',
            url_name='remove_favorite', permission_classes=[IsAuthenticated])
    def remove_favorite(self, request, pk=None):
        serializer = FavoriteCreteSerializer(data={'recipe': pk},
                                             context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorite = Favorite.objects.get(
            user=request.user,
            recipe=serializer.validated_data['recipe'])
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path='shopping_cart',
            url_name='add_to_shopping_cart',
            permission_classes=[IsAuthenticated])
    def add_shopping_cart(self, request, pk=None):
        serializer = ShoppingCartCreateSerializer(data={'recipe': pk},
                                                  context={'request': request})
        serializer.is_valid(raise_exception=True)
        shopping_cart = serializer.save(user=request.user)
        shopping_cart_data = RecipeMinifiedSerializer(
            shopping_cart.recipe,
            context={'request': request}).data
        return Response(
            data=shopping_cart_data,
            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path='shopping_cart',
            url_name='remove_from_shopping_cart',
            permission_classes=[IsAuthenticated])
    def remove_shopping_cart(self, request, pk=None):
        serializer = ShoppingCartCreateSerializer(
            data={'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorite = ShoppingCart.objects.get(
            user=request.user,
            recipe=serializer.validated_data['recipe'])
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        self.request.user.save()


class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeMinifiedSerializer
    pagination_class = None

    @action(detail=True, methods=['get'], url_path='shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, file_ext='pdf'):
        user = request.user
        current_user_shopping_list = Recipe.objects.filter(
            shopping_cart__user=user)
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
