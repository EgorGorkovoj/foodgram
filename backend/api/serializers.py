import pdb
import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from api.models import (Tag, Ingredient, Recipe, TagRecipe, ShortLinkRecipe,
                        RecipeIngredient, Favorites, ShoppingList)
from users.serializers import UserSerializer, ShortRecipeSerializer


class Base64ImageField(serializers.ImageField):
    """Кастомный класс для поля image."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
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
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)

    def to_representation(self, instance):
        """Метод для сериализации объекта модели."""
        ingredient = instance.ingredient
        serializers = IngredientSerializer(
            ingredient
        )
        data = serializers.data
        data['amount'] = instance.amount
        return data


class GetRicepeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredients'
    )
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
        return UserSerializer(obj.author, many=False).data

    def get_is_favorited(self, obj):
        """
        Метод для вычисления поля сериализатора is_favorited.
        Возращает True, если рецепт есть в избранном.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorites.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Метод для вычисления поля сериализатора is_in_shopping_cart.
        Возращает True, если рецепт есть в списке покупок.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredients'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'text',
            'image',
            'cooking_time',
        )

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        list_ingredients = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient.get('id'),
            )
            amount = ingredient.get('amount')
            list_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(list_ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        list_ingredients = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient.get('id'),
            )
            amount = ingredient.get('amount')
            list_ingredients.append(
                RecipeIngredient(
                    recipe=instance,
                    ingredient=current_ingredient,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(list_ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return GetRicepeSerializer(
            instance,
            context={'request': request}
        ).data


# class ShortLinkRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор избранных рецептов."""
#     short_link = serializers.URLField()

#     class Meta:
#         model = ShortLinkRecipe
#         fields = ('short-link', )

#     def create(self, validated_data):
#         request = self.context.get('request')
#         original_link = validated_data.pop('original_link')
#         short_link = validated_data.pop('short_url')
#         recipe = validated_data.pop('recipe')
#         ShortLinkRecipe.objects.get_or_create(short_link=short_link, recipe=recipe, original_link=original_link)
#         return


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorites
        fields = '__all__'

    def to_representation(self, instance):
        recipe = self.validated_data.get('recipe')
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingList
        fields = '__all__'

    def to_representation(self, instance):
        recipe = self.validated_data.get('recipe')
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data
