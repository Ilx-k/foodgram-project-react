from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag)
from users.models import FoodgramUser, Subscription
from recipes.validators import validate_name


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id',)


class FoodgramUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if request.user.is_authenticated:
            return user.subscribers.filter(author=obj).exists()
        else:
            return False


class SubscriptionSerializer(FoodgramUserSerializer):

    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    recipes = serializers.SerializerMethodField()

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            queryset = queryset[:int(recipes_limit)]
        return RecipeMinifiedSerializer(
            queryset, many=True, context=self.context
        ).data


class SubscriptionCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=FoodgramUser.objects.all()
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
            if Subscription.objects.filter(
                    author=author, user=user).exists():
                raise serializers.ValidationError(
                    detail='Вы уже подписаны на этого пользователя!')

        elif self.context['request'].method == 'DELETE':
            try:
                Subscription.objects.get(user=user, author=author)
            except Subscription.DoesNotExist:
                raise serializers.ValidationError('Подписка не найдена')
        return attrs

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author, context=self.context).data


class FavoriteCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    model = Favorite

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']
        if self.context['request'].method == 'POST':
            if self.model.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError('Рецепт уже добавлен')
        elif self.context['request'].method == 'DELETE':
            if not self.model.objects.filter(user=user,
                                             recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Рецепт не найден в добавленных'
                )
        return attrs

    def create(self, validated_data):
        return self.model.objects.create(**validated_data)


class ShoppingCartCreateSerializer(FavoriteCreateSerializer):
    model = ShoppingCart

    class Meta(FavoriteCreateSerializer.Meta):

        model = ShoppingCart


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[validate_name])

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[validate_name])

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__',


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
                                             source='ingredientes')
    image = Base64ImageField()
    author = FoodgramUserSerializer(read_only=True)
    name = serializers.CharField(validators=[validate_name])

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

    def validate(self, obj):
        for field in ['name', 'text', 'cooking_time', 'image']:
            if not obj.get(field):
                raise serializers.ValidationError(
                    f'{field} - Обязательное поле.'
                )
        tags = obj.get('tags', [])
        if not tags:
            raise serializers.ValidationError(
                'Поле тэгов не может быть пустым.')
        tag_ids = [tag.id for tag in tags]
        unique_tag_ids = set(tag_ids)
        if len(tag_ids) != len(unique_tag_ids):
            raise serializers.ValidationError(
                'Тэги должны быть уникальными.')

        ingredients = obj.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ингредиентов не может быть пустым')

        ingredient_ids = [item['ingredient'].id for item in ingredients]
        unique_ingredient_ids = set(ingredient_ids)
        if len(ingredient_ids) != len(unique_ingredient_ids):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )
        return obj

    def validate_cooking_time(self, value):
        if int(value) < 1:
            raise serializers.ValidationError(
                'Время готовки не должно быть меньше минуты')
        if int(value) > 1440:
            raise serializers.ValidationError(
                'Время готовки не должно быть больше суток')
        return value

    @atomic(durable=True)
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.save()
        return recipe

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
        existing_recipe_ingredients = instance.ingredientes.all()
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
