from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'Данный адрес электронной почты уже используется!',
        },
        max_length=254,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже существует!',
        },
        max_length=150,
        validators=([RegexValidator(regex=r'^[\w.@+-]+$')])
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        null=True,
        default=None,
        upload_to='users',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Класс Subscription."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Подписчик', related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Отслеживаемый автор рецепта', related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
