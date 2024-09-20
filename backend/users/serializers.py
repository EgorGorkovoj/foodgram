import base64

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.core.files.base import ContentFile

from users.models import User, Subscription


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

    class Meta:
        fields = ('user', 'author', )
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            )
        ]
