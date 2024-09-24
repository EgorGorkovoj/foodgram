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
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp' + ext)
        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Укороченный сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class PostUserSerializer(djoser_serializer.UserSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )
        model = CustomUser


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            'avatar',
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор кастомного пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    # avatar = serializers.HiddenField(default=AvatarSerializer)

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


# class TokenSerializer(djoser_serializer.TokenSerializer):

#     class Meta:
#         model = CustomUser
#         fields = ('password', 'email')

#     def validate(self, attrs):
#         email = CustomUser.objects.get()
#         password = attrs.get("password")
#         try:
#             validate_password(password, user)
#         except django_exceptions.ValidationError as e:
#             serializer_error = serializers.as_serializer_error(e)
#             raise serializers.ValidationError(
#                 {"password": serializer_error["non_field_errors"]}
#             )

#         return attrs


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField()
    # в модели Subscription и вернуть True.
    recipes = serializers.SerializerMethodField()  # список рецетов
    recipes_count = serializers.SerializerMethodField()  # количество рецптов
    avatar = ...  # Должно подгрузиться автоматом при наличии у пользователя.

    class Meta:
        model = CustomUser
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
        serializer = ShortRecipeSerializer(queryset, read_only=True, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


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
        serializer = SubscriptionListSerializer(
            instance.author,
            context={'request': request}
        )
        return serializer.data

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Подписаться на себя невозможно!'
            )
        return data
