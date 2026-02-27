from csv import DictReader

from django.core.management.base import BaseCommand

from reviews.models import Category, Comments, Genre, Review, Title, User


class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми данными'

    def check_fill_model(self, model):
        if model.objects.exists():
            print(f'{model.__name__} уже загружены')
            return True
        return False

    def handle(self, *args, **options):
        print('Загрузка данных')

        self.fill_users()
        self.fill_categories()
        self.fill_genres()
        self.fill_titles()
        self.fill_reviews()
        self.fill_comments()

    def fill_users(self):
        if self.check_fill_model(User):
            return

        with open('static/data/users.csv', encoding='utf-8') as file:
            for row in DictReader(file):
                User.objects.create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio']
                )
        print('Пользователи успешно загружены')

    def fill_categories(self):
        if self.check_fill_model(Category):
            return

        with open('static/data/category.csv', encoding='utf-8') as file:
            for row in DictReader(file):
                Category.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        print('Категории успешно загружены')

    def fill_genres(self):
        if self.check_fill_model(Genre):
            return

        with open('static/data/genre.csv', encoding='utf-8') as file:
            for row in DictReader(file):
                Genre.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        print('Жанры успешно загружены')

    def fill_titles(self):
        if self.check_fill_model(Title):
            return

        mapping = {}
        with open('static/data/genre_title.csv', encoding='utf-8') as file:
            for row in DictReader(file):
                mapping[row['title_id']] = row['genre_id']

        with open('static/data/titles.csv', encoding='utf-8') as file:
            for row in DictReader(file):
                Title.objects.create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=Category.objects.get(id=row['category']),
                    genre=Genre.objects.get(id=mapping.get(row['id'], None))
                )
        print('Произведения успешно загружены')

    def fill_reviews(self):
        if self.check_fill_model(Review):
            return

        with open('static/data/review.csv', encoding='utf-8') as file:
            for row in DictReader(file):
                Review.objects.create(
                    id=row['id'],
                    title=Title.objects.get(id=row['title_id']),
                    text=row['text'],
                    author=User.objects.get(id=row['author']),
                    score=row['score'],
                    pub_date=row['pub_date']
                )
        print('Обзоры успешно загружены')

    def fill_comments(self):
        if self.check_fill_model(Comments):
            return

        with open('static/data/comments.csv', encoding='utf-8') as file:
            for row in DictReader(file):
                Comments.objects.create(
                    id=row['id'],
                    review=Review.objects.get(id=row['review_id']),
                    text=row['text'],
                    author=User.objects.get(id=row['author']),
                    pub_date=row['pub_date']
                )
        print('Комментарии успешно загружены')
