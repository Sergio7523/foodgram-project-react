from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag
)
from recipes.utils import convert_txt
from users.serializers import RecipesBriefSerializer
from api.filters import IngredientSearchFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (
    CartSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    TagSerializer,
    WriteRecipeSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, IngredientSearchFilter,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    paginations_class = CustomPagination
    permission_classes = (AuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return WriteRecipeSerializer
        return ReadRecipeSerializer

    def add_or_del_object(self, model, pk, serializer, errors):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={'user': self.request.user.id, 'recipe': recipe.id}
        )
        if self.request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipesBriefSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        object = model.objects.filter(user=self.request.user, recipe=recipe)
        if not object.exists():
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        errors = 'В избранном нет рецепта.'
        return self.add_or_del_object(Favorite, pk, FavoriteSerializer, errors)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        errors = 'В списке покупок нет рецепта.'
        return self.add_or_del_object(Cart, pk, CartSerializer, errors)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return convert_txt(ingredients)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return recipe.favorites.all()
