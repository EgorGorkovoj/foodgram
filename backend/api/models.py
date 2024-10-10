from django.db import models
from django.core.validators import MinValueValidator

from users.models import CustomUser


class Tag(models.Model):
    """Модель Tag."""
    name = models.CharField(
        verbose_name='Название',
        max_length=32,
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=32,
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
        max_length=128,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=64,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Recipe."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        through='TagRecipe',
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
        max_length=256,
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """
    Промежуточная модель связи ManyToMany
    для моделей Recipe и Tag.
    """
    recipe = models.ForeignKey(
        Recipe, related_name='tagrecipe', on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag, related_name='tagrecipe',
        on_delete=models.SET_DEFAULT,
        default=None,
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


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
    original_link = models.URLField()
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
        CustomUser, on_delete=models.CASCADE, related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe, related_name='favorites', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное.'


class ShoppingList(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='shoppinglist',
    )
    recipe = models.ForeignKey(
        Recipe, related_name='shoppinglist', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок.'
