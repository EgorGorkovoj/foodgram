from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

from core.constants import USER_LENGTH, EMAIL_MAX_LENGTH, REGEX_VALID


class User(AbstractUser):
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
        max_length=EMAIL_MAX_LENGTH,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже существует!',
        },
        max_length=USER_LENGTH,
        validators=([RegexValidator(regex=REGEX_VALID)])
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=USER_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=USER_LENGTH,
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
        User, on_delete=models.CASCADE,
        verbose_name='Подписчик', related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Отслеживаемый автор рецепта', related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
