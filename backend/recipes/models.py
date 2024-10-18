from django.db import models
from django.core.validators import MinValueValidator

from users.models import User
from core.constants import (TAG_LENGTH, INGREDIENT_NAME_MAX_LENGTH,
                            MEASUREMENT_UNIT_MAX_LENGTH,
                            RECIPE_NAME_MAX_LENGTH)


class Tag(models.Model):
    """Модель Tag."""
    name = models.CharField(
        verbose_name='Название',
        max_length=TAG_LENGTH,
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=TAG_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ingredient."""

    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = ('name', )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Recipe."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=RECIPE_NAME_MAX_LENGTH,
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель связи ManyToMany
    для моделей Recipe и Ingredient.
    """
    ingredient = models.ForeignKey(
        Ingredient, related_name='recipeingredients', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, related_name='recipeingredients', on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество в рецепте',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class ShortLinkRecipe(models.Model):
    """Модель короткой ссылки рецепта."""
    recipe = models.OneToOneField(
        Recipe, on_delete=models.CASCADE, related_name='shortlink',
    )
    original_link = models.URLField(verbose_name='Ссылка на рецепт')
    short_link = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Короткая ссылка',
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return f'{self.recipe} - {self.short_link} - {self.original_link}'


class Favorites(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe, related_name='favorites', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorites'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное.'


class ShoppingList(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shoppinglist',
    )
    recipe = models.ForeignKey(
        Recipe, related_name='shoppinglist', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shoppinglist'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок.'
