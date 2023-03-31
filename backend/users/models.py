from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        validators=(
            UnicodeUsernameValidator(),
        )
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} (email: {self.email})'


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_cannot_follow_yourself'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
