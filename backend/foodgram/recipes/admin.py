from django.contrib import admin

from foodgram.settings import EMPTY_VALUE_DISPLAY
from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe
)


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY
    inlines = (IngredientRecipeInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY
    ordering = ('name',)
    inlines = (TagRecipeInline,)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'get_tags', 'count_favorites')
    list_filter = ('tags', 'author', 'name')
    search_fields = ('name', 'author__username', 'author__email', 'tags__name')
    empty_value_display = EMPTY_VALUE_DISPLAY
    filter_vertical = ('tags',)
    ordering = ('name',)
    inlines = (TagRecipeInline, IngredientRecipeInline,)

    def count_favorites(self, obj):
        return obj.favorites.count()

    def get_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    search_fields = ('recipe__name', 'user__username', 'user__email')
    empty_value_display = EMPTY_VALUE_DISPLAY


class CartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    search_fields = ('user__username', 'user__email')
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Cart, CartAdmin)
