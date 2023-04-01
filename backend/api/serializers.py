from base64 import b64decode
from re import match, search

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from rest_framework import serializers
from rest_framework.serializers import (BooleanField, CharField, ImageField,
                                        ModelSerializer, ValidationError)
from rest_framework.status import HTTP_400_BAD_REQUEST
from users.models import Subscriptions, User


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )

    def validate_color(self, color):
        if not search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
            raise ValidationError(
                detail=f'{color} не является hex цветом'
            )
        return f'{color}'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RegistreUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'username', 'password')
        write_only_field = ('password',)

    def validate_username(self, value):
        if not match(r'[\w.@+\-]+', value):
            raise ValidationError('Некорректный логин')
        return value


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        write_only_field = ('password',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=request.user,
            author=obj.id
        ).exists()


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise ValidationError(
                detail='Пользователь не может подписаться сам на себя',
                code=HTTP_400_BAD_REQUEST
            )
        if Subscriptions.objects.filter(
            user=user,
            author=author
        ).exists():
            raise ValidationError(
                detail=('Пользователь не может подписаться '
                        'на другого пользователя дважды'),
                code=HTTP_400_BAD_REQUEST
            )
        return data


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipeSerializer(ModelSerializer):
    id = CharField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='recipeingredient_set',
    )
    author = CustomUserSerializer(read_only=True)
    is_favorited = BooleanField(read_only=True, default=None)
    is_in_shopping_cart = BooleanField(read_only=True, default=None)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def create(self, validated_data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(tag_id=tag, recipe=recipe)

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags = self.initial_data.get('tags')
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeTag.objects.bulk_create(
            RecipeTag(
                tag_id=tag,
                recipe=instance,

            ) for tag in tags)

        ingredients = self.initial_data.get('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

        instance.save()
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients:
            raise ValidationError(
                {'ingredients': ('В рецепте должен быть использован '
                                 'минимум один ингредиент')
                 }
            )
        array_of_ingredients = []
        for ingredient in ingredients:

            if ingredient['id'] in array_of_ingredients:
                raise ValidationError(
                    detail='Ингридиенты не должны повторяться',
                    code=HTTP_400_BAD_REQUEST
                )
            if int(ingredient.get('amount')) < 1:
                raise ValidationError(
                    {'amount': 'Количество должно быть больше 0'},
                    code=HTTP_400_BAD_REQUEST
                )
            array_of_ingredients.append(ingredient['id'])
        if not tags:
            raise ValidationError(
                {'tags': ('Нужно выбрать хотя бы один тег')
                 }
            )
        array_of_tags = set(tags)
        if len(array_of_tags) != len(tags):
            raise ValidationError(
                detail='Теги должны быть уникальными',
                code=HTTP_400_BAD_REQUEST
            )
        return data
