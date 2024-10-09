from django.shortcuts import get_object_or_404

from rest_framework import serializers

from api.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                        Favorites, ShoppingList)
from core.serializers import Base64ImageField
from users.serializers import UserSerializer, ShortRecipeSerializer


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
    """
    Вспомогательный сериализатор рецептов.
    В основном используется для правильного отображения рецептов
    при GET запросах.
    """

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
        """Метод для получения автора рецепта."""
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

    def validate_tags(self, data):
        if len(data) < 1:
            raise serializers.ValidationError(
                'Поле должно содержать хотя бы 1 тег!'
            )
        tags_list = []
        for tag in data:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Теги не могут повторяться!'
                )
            tags_list.append(tag)
        return data

    def validate_ingredients(self, data):
        if len(data) < 1:
            raise serializers.ValidationError(
                'Рецепт не может быть без ингредиентов.'
            )
        ingredient_list = []
        for ingredient in data:
            check = Ingredient.objects.filter(id=ingredient['id']).exists()
            if not check:
                raise serializers.ValidationError(
                    'Такого ингредиента не существует!'
                )
            if ingredient['amount'] == 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0!'
                )
            if ingredient['id'] in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторяться!'
                )
            ingredient_list.append(ingredient['id'])
        return data

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
        if 'ingredients' not in self.initial_data \
                or 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                'Поле ingredients обязательно!'
            )
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        list_ingredients = []
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('id')
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
