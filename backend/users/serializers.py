import base64

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.core.files.base import ContentFile

from api.models import Recipe
from users.models import User, Subscription
from api.serializers import RecipeShortSerializer


class Base64ImageField(serializers.ImageField):
    """Кастомный класс для поля image."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp' + ext)
        return super().to_internal_value(data)


class PostUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = (
            'avatar',
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор кастомного пользователя."""
    is_subscribed = serializers.SerializerMethodField()
    # avatar = serializers.HiddenField(default=AvatarSerializer)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Метод для вычисления поля сериализатора is_subscribed.
        Возращает True, если пользователь подписан на автора рецета.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return Subscription.objects.filter(
                user=request.user, author_recipe=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField()
    # в модели Subscription и вернуть True.
    recipes = serializers.SerializerMethodField()  # список рецетов
    recipes_count = serializers.SerializerMethodField()  # количество рецптов
    avatar = ...  # Должно подгрузиться автоматом при наличии у пользователя.

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
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is not None and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.query_params.get('recipes_limit'):
            recipes_limit = int(request.query_params.get('recipes_limit'))
            queryset = Recipe.objects.filter(author=obj.author)[:recipes_limit]
        queryset = Recipe.objects.filter(author=obj.author)
        serializer = RecipeShortSerializer(queryset, read_only=True, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()








# class SubscriptionSerializer(serializers.ModelSerializer):
#     """Сериализатор подписки."""

#     class Meta:
#         fields = ('user', 'author', )
#         model = Subscription
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=('user', 'author')
#             )
#         ]
