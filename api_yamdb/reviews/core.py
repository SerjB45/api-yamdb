from django.db import models


MAX_SCORE = 10
MIN_SCORE = 1


class CommonSlugModel(models.Model):
    name = models.CharField(max_length=256, verbose_name='Наименование',)
    slug = models.SlugField(unique=True, verbose_name='Идентификатор',)

    class Meta:
        abstract = True


class CommonPublicationModel(models.Model):
    text = models.TextField(verbose_name='Текст',)
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации',)

    class Meta:
        abstract = True
