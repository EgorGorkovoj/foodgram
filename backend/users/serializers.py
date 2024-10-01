import base64

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.core.files.base import ContentFile

from djoser import serializers as djoser_serializer

from api.models import Recipe
from users.models import CustomUser, Subscription


class Base64ImageField(serializers.ImageField):
    """Кастомный класс для поля image."""
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Укороченный сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# class PostUserSerializer(djoser_serializer.UserSerializer):
#     """Сериализатор для создания пользователя."""

#     class Meta:
#         fields = (
#             'id',
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#         )
#         model = CustomUser


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            'avatar',
        )


class UserSerializer(djoser_serializer.UserSerializer):
    """Сериализатор кастомного пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        model = CustomUser

    def get_is_subscribed(self, obj):
        """
        Метод для вычисления поля сериализатора is_subscribed.
        Возращает True, если пользователь подписан на автора рецета.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return Subscription.objects.filter(
                user=request.user, author=obj).exists()
        return False


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField()
    # в модели Subscription и вернуть True.
    recipes = serializers.SerializerMethodField()  # список рецетов
    recipes_count = serializers.SerializerMethodField()  # количество рецптов
    # avatar = ...  # Должно подгрузиться автоматом при наличии у пользователя.

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
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
        if request is not None or request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True,
                                     context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        fields = ('user', 'author', )
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            )
        ]

    def to_representation(self, instance):
        """Метод для сериализации объекта модели."""
        request = self.context.get('request')
        author = self.validated_data.get('author')
        serializer = SubscriptionListSerializer(
            author, context={'request': request}
        )
        return serializer.data

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                {'Error': 'Подписаться на себя невозможно!'}
            )
        return data
