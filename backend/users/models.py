from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F, CheckConstraint, UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator

from recipes.validators import validate_name
from recipes.constants import (NAME_LENGTH, EMAIL_LENGTH)


class FoodgramUser(AbstractUser):

    username = models.CharField(
        verbose_name=_('Логин'),
        validators=[UnicodeUsernameValidator()],
        max_length=NAME_LENGTH,
        unique=True
    )
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_('Имя'),
        validators=(validate_name,),
        max_length=NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        verbose_name=_('Фамилия'),
        validators=(validate_name,),
        max_length=NAME_LENGTH,
        blank=False
    )
    following = models.ManyToManyField(
        "self",
        through='Subscription',
        through_fields=('user', 'author'),
        symmetrical=False,
        related_name='following_relationships'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'password', 'username')

    class Meta:
        app_label = 'users'
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('id',)

    def __str__(self):
        return self.email


class Subscription(models.Model):

    user = models.ForeignKey(
        FoodgramUser,
        verbose_name=_('Подписчик'),
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    author = models.ForeignKey(
        FoodgramUser,
        verbose_name=_('Автор'),
        on_delete=models.CASCADE,
        related_name='followed_by'
    )

    class Meta:
        verbose_name = _('Подписчик')
        verbose_name_plural = _('Подписчики')
        ordering = ('id',)
        constraints = [
            CheckConstraint(check=~Q(user=F('author')),
                            name='not_following_itself'),
            UniqueConstraint(
                fields=['user', 'author'], name='unique_subscribe'
            ),
        ]

    def __str__(self):
        return f'{self.user} >> {self.author}'
