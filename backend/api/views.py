from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscriptions, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('^name',)
    filterset_class = IngredientFilter


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        follows = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            if not serializer.is_valid():
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
            Subscriptions.objects.create(
                user=request.user,
                author=author
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        if not Subscriptions.objects.filter(
            user=request.user,
            author=author
        ).exists():
            return Response(
                {'errors': 'Данной подписки нет'},
                status=HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.filter(
            user=request.user,
            author=author
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):

    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        favorites = Favorites.objects.filter(user=user, recipe=OuterRef('pk'))
        shopping_cart = ShoppingCart.objects.filter(
            user=user, recipe=OuterRef('pk')
        )
        return Recipe.objects.select_related(
            'author').prefetch_related('ingredients').annotate(
            is_favorited=Exists(favorites),
            is_in_shopping_cart=Exists(shopping_cart)
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def send_message(ingredients):
        filename = 'shopping_list.txt'
        shopping_list = (
            'Список покупок:\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient__name"]}: {ing["amount"]}'
                f' {ing["ingredient__measurement_unit"]}\n'
            )
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        if not ShoppingCart.objects.filter(
                user=request.user
        ).exists():
            return Response(
                {'errors': 'В корзине пусто'},
                status=HTTP_400_BAD_REQUEST
            )
        ingredients = RecipeIngredient.objects.filter(
            recipe__baskets__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(recipe)
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Этот рецепт уже в списке покупок'},
                    status=HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=HTTP_201_CREATED)

        ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(recipe)
            if Favorites.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Этот рецепт уже в избранном'},
                    status=HTTP_400_BAD_REQUEST
                )
            Favorites.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=HTTP_201_CREATED)

        Favorites.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)
