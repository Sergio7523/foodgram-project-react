from rest_framework import serializers
from rest_framework.serializers import CharField, EmailField, ModelSerializer
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from djoser.serializers import UserCreateSerializer

from foodgram.settings import LIMIT
from recipes.models import Recipe
from users.models import Follow, User


FIELDS = (
    'id',
    'email',
    'username',
    'first_name',
    'last_name',
)


class UserSerializer(ModelSerializer):
    """Сериализатор для получения информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = FIELDS + ('is_subscribed',)

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
        fields = FIELDS + ('password',)
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

    def validate_author(self, value):
        """Валидация данных."""
        author = value
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя.'}
            )
        return value

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


class ResponeSubscribeSerializer(UserSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Получение списка рецептов автора."""
        request = self.context.get('request')
        recipes_limit = request.POST.get('recipes_limit', LIMIT)
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:(recipes_limit)]
        return RecipesBriefSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Подсчет рецептов."""
        return obj.recipes.all().count()
