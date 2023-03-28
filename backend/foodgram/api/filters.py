from django_filters import rest_framework as filter
from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from users.models import User


class RecipeFilter(filter.FilterSet):
    is_favorited = filter.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filter.BooleanFilter(
        method='filter_is_in_shopping_cart')
    author = filter.ModelChoiceFilter(queryset=User.objects.all())
    tags = filter.AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
