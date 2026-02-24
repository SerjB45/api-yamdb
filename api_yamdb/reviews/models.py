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


class Categories(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


class Titles(models.Model):
    name = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    category = models.ForeignKey(
        Categories,
        on_delete=models.CASCADE,
        related_name='category_title'
    )


class Genres(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


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
