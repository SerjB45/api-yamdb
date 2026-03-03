from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .core import (
    CommonPublicationModel,
    CommonSlugModel,
    MAX_SCORE,
    MIN_SCORE,

)

TEXT_CHARACTER_LIMIT = 10


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    USERS_ROLE = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email адрес',
    )
    role = models.CharField(
        max_length=10,
        choices=USERS_ROLE,
        default=USER,
        verbose_name='Роль',
    )
    bio = models.TextField(blank=True, verbose_name='Биография',)

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == self.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class Category(CommonSlugModel):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:TEXT_CHARACTER_LIMIT]


class Genre(CommonSlugModel):

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:TEXT_CHARACTER_LIMIT]


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Наименование',)
    year = models.PositiveSmallIntegerField(verbose_name='Год',)
    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='titles',
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='titles',
        verbose_name='Жанр',
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Название'
        verbose_name_plural = 'Названия'

    def __str__(self):
        return self.name[:TEXT_CHARACTER_LIMIT]


class Review(CommonPublicationModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MaxValueValidator(MAX_SCORE),
            MinValueValidator(MIN_SCORE)
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review_title_author',
            ),
        ]

    def __str__(self):
        return self.text[:TEXT_CHARACTER_LIMIT]


class Comment(CommonPublicationModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Обзор',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:TEXT_CHARACTER_LIMIT]
