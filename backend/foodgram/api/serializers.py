from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from foodgram.settings import (
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag
)
from users.serializers import UserSerializer


class IngredientSerializer(ModelSerializer):
    """Сериализатор модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(ModelSerializer):
    """Сериализатор модели IngredientRecipe."""
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class WriteIngredientRecipeSerializer(ModelSerializer):
    """Сериализатор для записи модели IngredientRecipe."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class TagSerializer(ModelSerializer):
    """Сериализатор модели Tag."""
    name = serializers.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        validators=(UniqueValidator(Tag.objects.all()),)
    )
    slug = serializers.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        validators=(UniqueValidator(Tag.objects.all()),)
    )

    class Meta:
        model = Tag
        fields = '__all__'


class ReadRecipeSerializer(ModelSerializer):
    """Сериализатор для получения информации из модели Recipe."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredientrecipes',
        read_only=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

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
        read_only_fields = fields

    def get_is_favorited(self, obj):
        """Рецепт в избранном или нет."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Рецепт в корзине или нет."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(user=request.user, recipe=obj).exists()


class WriteRecipeSerializer(ModelSerializer):
    """Сериализатор для записи модели Recipe."""
    ingredients = WriteIngredientRecipeSerializer(
        many=True,
        source='ingredientrecipes',
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create_ingredient_amount(self, ingredients, recipe):
        """Создание записей ингредиент - рецепт - количество."""
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = ingredient['id']
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта."""
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipes')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient_amount(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.create_ingredient_amount(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class FavoriteSerializer(ModelSerializer):
    """Сериализатор модели Favorite."""
    user = UserSerializer
    recipe = ReadRecipeSerializer

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже есть в избранном.'
            ),
        )

    def validate(self, data):
        """Валидация данных"""
        user = data.get('user')
        recipe = data.get('recipe')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Данный рецепт уже есть в избранном.'}
            )
        return data

    def create(self, validated_data):
        """Создание записи favorite"""
        user = validated_data.get('user')
        recipe = validated_data.get('recipe')
        return Favorite.objects.create(user=user, recipe=recipe)
