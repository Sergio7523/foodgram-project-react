from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag
)
from recipes.utils import convert_txt
from users.serializers import RecipesBriefSerializer
from api.filters import IngredientSearchFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import AuthorOrAdminOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    TagSerializer,
    WriteRecipeSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, IngredientSearchFilter,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    paginations_class = CustomPagination
    permission_classes = (AuthorOrAdminOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериалайзера в зависимости от запроса."""
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return WriteRecipeSerializer
        return ReadRecipeSerializer

    def add_recipe(self, model, request, pk):
        """Добавление рецепта."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        _, created = model.objects.get_or_create(recipe=recipe, user=user)
        if not created:
            raise ValidationError('Такой рецепт уже существует!')
        serializer = RecipesBriefSerializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        """Удаление рецепта."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавление и удаление рецептов в избранное."""
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, pk)
        else:
            return self.delete_recipe(Favorite, request, pk)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецептов в список покупок."""
        if request.method == 'POST':
            return self.add_recipe(Cart, request, pk)
        else:
            return self.delete_recipe(Cart, request, pk)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return convert_txt(ingredients)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет избранного."""
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Информация о рецептах в избранном."""
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return recipe.favorites.all()
