from django.contrib import admin

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
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'
    inlines = (IngredientRecipeInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    inlines = (TagRecipeInline,)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'get_tags', 'count_favorites')
    list_filter = ('tags',)
    search_fields = ('name', 'author__username', 'author__email', 'tags__name')
    empty_value_display = '-пусто-'
    filter_vertical = ('tags',)
    inlines = (TagRecipeInline, IngredientRecipeInline,)

    def count_favorites(self, obj):
        return obj.favorites.count()

    def get_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    search_fields = ('recipe__name', 'user__username', 'user__email')
    empty_value_display = '-пусто-'


class CartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    search_fields = ('user__username', 'user__email')
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Cart, CartAdmin)
