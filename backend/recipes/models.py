from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.TextField(
        verbose_name='Тег',
        max_length=200,
        unique=True
    )
    color = ColorField(
        max_length=7,
        default='#ffffff',
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Наименование тега',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    name = models.TextField(
        'Наименование рецепта', max_length=200
    )
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipes/images'
                              )
    text = models.TextField(
        verbose_name='Описание рецепта', max_length=200
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиент',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        through='RecipeTag'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления', validators=(MinValueValidator(1),)
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        verbose_name = 'Связь ингредиентов и рецептов'
        verbose_name_plural = 'Связь ингредиентов и рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='связи ингредиента и рецепта'
            )
        ]

    def __str__(self):
        return f'Ингредиент {self.ingredient} связан с рецептом {self.recipe}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Связь тегов и рецептов'
        verbose_name_plural = 'Связь тегов и рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='Уникальность связи тега и рецепта'
            )
        ]

    def __str__(self):
        return f'Тег {self.tag} связан с рецептом {self.recipe}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourites'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='baskets',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='baskets',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Нельзя добавить рецепт в корзину дважды'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину рецепт {self.recipe}'
