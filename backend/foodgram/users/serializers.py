from rest_framework import serializers
from rest_framework.serializers import CharField, EmailField, ModelSerializer
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from djoser.serializers import UserCreateSerializer

from foodgram.settings import LIMIT
from recipes.models import Recipe
from users.models import Follow, User


class UserSerializer(ModelSerializer):
    """Сериализатор для получения информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = '__all__'

    def get_is_subscribed(self, obj):
        """Подписка на автора."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    username = CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class FollowSerializer(ModelSerializer):
    """Сериализатор подписки на пользователя."""
    author = UserSerializer
    user = UserSerializer

    class Meta:
        model = Follow
        fields = ('author', 'user')
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на данного пользователя.'
            ),
        )

    def validate(self, data):
        """Валидация данных."""
        author = data.get('author')
        user = data.get('user')
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя.'}
            )
        return data

    def create(self, validated_data):
        """Создание записи подписки."""
        author = validated_data.get('author')
        user = validated_data.get('user')
        return Follow.objects.create(user=user, author=author)


class RecipesBriefSerializer(ModelSerializer):
    """Сериализатор для получения информации о рецепте."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')
        read_only_fields = fields


class ResponeSubscribeSerializer(ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        """Статус подписки на автора."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        """Получение списка рецептов автора."""
        request = self.context.get('request')
        recipes_limit = request.POST.get('recipes_limit') or LIMIT
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:(recipes_limit)]
        return RecipesBriefSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Подсчет рецептов."""
        return obj.recipes.all().count()
