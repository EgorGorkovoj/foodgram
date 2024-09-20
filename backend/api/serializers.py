import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from api.models import (Tag, Ingredient, Recipe,
                        RecipeIngredient, Favorites, ShoppingList)
from users.serializers import UserSerializer


class Base64ImageField(serializers.ImageField):
    """Кастомный класс для поля image."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор промежуточной модели RecipeIngredientSerializer.
    Необходим для правильного отображения поля ингредиентов в модели Recipe.
    """

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe."""
    tags = TagSerializer(many=True)
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'image',
            'cooking_time',
        )

    def get_author(self, obj):
        return UserSerializer(many=False)

# Проверить, надо ли добавить request.user.is_autheticated!
    def get_is_favorited(self, obj):
        """
        Метод для вычисления поля сериализатора is_favorited.
        Возращает True, если рецепт есть в избранном.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return Favorites.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

# Проверить, надо ли добавить request.user.is_autheticated!
    def get_is_in_shopping_cart(self, obj):
        """
        Метод для вычисления поля сериализатора is_in_shopping_cart.
        Возращает True, если рецепт есть в списке покупок.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return ShoppingList.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

# Проверить будет ли добавляться amount.
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient)
            RecipeIngredient.objects.create(ingredients=current_ingredient,
                                            recipe=recipe
                                            )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Укороченный сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorites
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingList
        fields = '__all__'
