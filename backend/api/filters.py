from django.contrib.auth import get_user_model
from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import FilterSet, filters
from django_filters.rest_framework.filters import (AllValuesMultipleFilter,
                                                   BooleanFilter,
                                                   ModelChoiceFilter)
from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(FilterSet):
    """Фильтр по названию ингредиента"""
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):

        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-startswith')


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = BooleanFilter(method='is_in_shopping_cart_filter')

    def is_favorited_filter(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(baskets__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
