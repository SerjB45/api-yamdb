from django.contrib.auth.models import AbstractUser
from django.db import models


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


class Categories(models.Model):
    name = models.CharField(max_length=255, verbose_name='Категория',)
    slug = models.SlugField(unique=True, verbose_name='Идентификатор',)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genres(models.Model):
    name = models.CharField(max_length=255, verbose_name='Жанр',)
    slug = models.SlugField(unique=True, verbose_name='Идентификатор',)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Titles(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование',)
    year = models.PositiveSmallIntegerField(verbose_name='Год',)
    category = models.ForeignKey(
        Categories,
        on_delete=models.DO_NOTHING,
        related_name='category_title',
        verbose_name='Категория',
    )
    genre = models.ForeignKey(
        Genres,
        on_delete=models.DO_NOTHING,
        blank=True,
        related_name='genre_title',
        verbose_name='Жанр',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Название'
        verbose_name_plural = 'Названия'


class Reviews(models.Model):
    title_id = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name='title',
        verbose_name='ID произведения',
    )
    text = models.TextField(verbose_name='Обзор',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Автор обзора',
    )
    score = models.PositiveSmallIntegerField(verbose_name='Оценка',)
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации',)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'


class Comments(models.Model):
    review_id = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name='rev_comment',
        verbose_name='ID обзора',
    )
    text = models.TextField(verbose_name='Комментарий',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_comment',
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
