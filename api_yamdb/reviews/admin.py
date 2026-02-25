from django.contrib import admin

from .models import Categories, Comments, Genres, Reviews, Titles, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
    )


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Titles)
class TitlesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category',
    )


@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = (
        'title_id',
        'author',
        'pub_date',
    )


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = (
        'review_id',
        'author',
        'pub_date',
    )
