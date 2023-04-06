from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from foodgram.settings import (
    FIRST_AND_LAST_NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH
)


class User(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Недопустимые символы в имени пользователя'
            ),
        )
    )
    first_name = models.CharField(
        max_length=FIRST_AND_LAST_NAME_MAX_LENGTH,
        verbose_name='имя',
    )
    last_name = models.CharField(
        max_length=FIRST_AND_LAST_NAME_MAX_LENGTH,
        verbose_name='фамилия',
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=('user', 'author'), name='follow_unique'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
