from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from djoser import serializers as djoser_serializer

from core.serializers import Base64ImageField, ShortRecipeSerializer
from users.models import User, Subscription


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
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
        model = User

    def get_is_subscribed(self, obj):
        """
        Метод для вычисления поля сериализатора is_subscribed.
        Возращает True, если пользователь подписан на автора.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
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
        """
        Метод для вычисления поля сериализатора is_subscribed.
        Возращает True, если пользователь подписан на автора.
        """
        request = self.context.get('request')
        if request is not None or request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        """
        Метод для вычисления поля сериализатора recipes.
        Возвращает сериализованные рецепты автора на которого подписались.
        Дополнительно сделана возможность фильтрации
        по параметру 'recipes_limit'.
        """
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
        """Метод возвращающий количество рецптов."""
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
