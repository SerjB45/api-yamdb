from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERS_ROLE = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=USERS_ROLE,
        default='user',
    )

    bio = models.TextField('Биография', blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username


class Categories(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    category = models.ForeignKey(
        Categories,
        on_delete=models.DO_NOTHING,
        related_name='category_title'
    )
    genre = models.ForeignKey(
        Genres,
        on_delete=models.DO_NOTHING,
        blank=True,
        related_name='genre_title'
    )

    def __str__(self):
        return self.name


class Reviews(models.Model):
    title_id = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name='title'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review'
    )
    score = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        return self.text


class Comments(models.Model):
    review_id = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name='rev_comment'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_comment'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        return self.text
