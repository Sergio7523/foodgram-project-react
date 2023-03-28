from django.core.validators import MinValueValidator
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from foodgram.settings import (
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT
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
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class WriteIngredientRecipeSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=MIN_INGREDIENT_AMOUNT,
                message=(f'{MIN_INGREDIENT_AMOUNT} ингредиент минимум.')
            ),
        )
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class TagSerializer(ModelSerializer):
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
        fields = ('id', 'name', 'color', 'slug',)


class ReadRecipeSerializer(ModelSerializer):
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
            'ingredients',
            'name',
            'author',
            'text',
            'image',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(user=request.user, recipe=obj).exists()


class WriteRecipeSerializer(ModelSerializer):
    ingredients = WriteIngredientRecipeSerializer(
        many=True,
        source='ingredientrecipes',
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=MIN_COOKING_TIME,
                message=(f'Минимум: {MIN_COOKING_TIME} минута')
            ),
        )
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'name',
            'tags',
            'text',
            'image',
            'cooking_time'
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipes')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient.get('amount')
            base_ingredient = ingredient.get('id')
            if (
                IngredientRecipe.objects.filter(
                    recipe=recipe, ingredient=base_ingredient
                ).exists()
            ):
                raise serializers.ValidationError(
                    {'errors': 'Одинаковые ингредиенты недопустимы'}
                )
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=base_ingredient, amount=amount
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipes')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            base_ingredient = ingredient.get('id')
            if (
                IngredientRecipe.objects.filter(
                    recipe=instance, ingredient=base_ingredient
                ).exists()
            ):
                raise serializers.ValidationError(
                    {'errors': 'Одинаковые ингредиенты недопустимы'}
                )
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=base_ingredient, amount=amount
            )
        instance.save()
        return instance


class FavoriteSerializer(ModelSerializer):
    user = UserSerializer
    recipe = ReadRecipeSerializer

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в избранном.'
            ),
        )

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен в избранное.'}
            )
        return data

    def create(self, validated_data):
        user = validated_data.get('user')
        recipe = validated_data.get('recipe')
        return Favorite.objects.create(user=user, recipe=recipe)


class CartSerializer(ModelSerializer):
    user = UserSerializer
    recipe = ReadRecipeSerializer

    class Meta:
        model = Cart
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок.'
            ),
        )

    def create(self, validated_data):
        user = validated_data.get('user')
        recipe = validated_data.get('recipe')
        return Cart.objects.create(user=user, recipe=recipe)
