from django.contrib import admin
from django.contrib.admin import register

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')

    def count_favorites(self, obj):
        return obj.favorites.count()


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    pass


@register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


@register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    pass
