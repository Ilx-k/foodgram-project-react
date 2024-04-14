import base64
import uuid

from django.core.files.base import ContentFile
from django.db.transaction import atomic
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from rest_framework import serializers
from users.models import CustomUser, Subscription
from recipes.constants import SCORE_MIN, SCORE_MAX


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]
            if ext.lower() not in ('jpeg', 'jpg', 'png'):
                raise serializers.ValidationError(
                    'Формат изображения не поддерживается. \
                    Используйте форматы JPEG или PNG.')

            uid = uuid.uuid4()
            data = ContentFile(
                base64.b64decode(img_str), name=uid.urn[9:] + '.' + ext
            )

        return super(Base64ImageField, self).to_internal_value(data)


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id',)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscription.objects.filter(user=user, author=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscription.objects.filter(user=user,
                                           author=obj.author).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return RecipeMinifiedSerializer(recipes, many=True,
                                        context=self.context).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscriptionCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, attrs):
        user = self.context['request'].user
        author = attrs['author']
        if self.context['request'].method == 'POST':
            if user == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя'
                )
        elif self.context['request'].method == 'DELETE':
            try:
                Subscription.objects.get(user=user, author=author)
            except Subscription.DoesNotExist:
                raise serializers.ValidationError('Подписка не найдена')
        return attrs

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)


class FavoriteCreteSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']
        if self.context['request'].method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError('Рецепт уже в избранном')
        elif self.context['request'].method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Рецепт не найден в избранных'
                )
        return attrs

    def create(self, validated_data):
        return Favorite.objects.create(**validated_data)


class ShoppingCartCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']

        if self.context['request'].method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Рецепт уже в корзине')
        elif self.context['request'].method == 'DELETE':
            if not ShoppingCart.objects.filter(user=user,
                                               recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Рецепт не найден в корзине')
        return attrs

    def create(self, validated_data):
        return ShoppingCart.objects.create(**validated_data)


class CustomUserSignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        instance = super().create(validated_data)
        instance.set_password(password)
        instance.save()
        return instance


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers. ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredients')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество не должно быть меньше 1'
            )
        if value > 100000:
            raise serializers.ValidationError(
                'Количество не должно быть больше 100000'
            )
        return value


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all(),
                                              required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        extra_kwargs = {
            'ingredients': {'required': True, 'allow_blank': False},
            'tags': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'image': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Поле ингредиентов не может быть пустым!"}
            )
        if (len(set(item['id'] for item in ingredients)) != len(ingredients)):
            raise serializers.ValidationError(
                'Ингридиенты не должны повторяться!')
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Поле тегов не может быть пустым!"}
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться!"}
            )
        return data

    def validate_cooking_time(self, value):
        if int(value) < SCORE_MIN:
            raise serializers.ValidationError(
                'Время готовки не должно быть меньше минуты')
        if int(value) > SCORE_MAX:
            raise serializers.ValidationError(
                'Время готовки не должно быть больше суток')
        return value

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                {"image": "Поле изображения не может быть пустым!"}
            )
        return image

    @atomic(durable=True)
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        _ = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        instance.tags.set(tags)

        recipe_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return instance

    @atomic(durable=True)
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image.delete()
        instance.image = validated_data.get('image', instance.image)

        new_tags = validated_data.pop('tags', [])
        instance.tags.set(new_tags)

        new_ingredients_data = validated_data.pop('ingredients', [])
        existing_recipe_ingredients = instance.recipe_ingredients.all()
        existing_recipe_ingredients.delete()

        recipe_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ) for ingredient_data in new_ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
