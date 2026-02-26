import csv

from django.core.management.base import BaseCommand

from reviews.models import Category, Comments, Genre, Review, Title, User

DATA_DIR = 'static/data/'


class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми данными'

    def handle(self, *args, **options):
        print('Загрузка данных')

        self.fill_users()
        self.fill_categories()
        self.fill_genres()
        self.fill_titles()
        self.fill_reviews()
        self.fill_comments()

    def fill_users(self):
        if User.objects.exists():
            print('Пользователи уже загружены')
            return

        file_path = DATA_DIR + 'users.csv'
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                User.objects.create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio']
                )
        print('Пользователи успешно загружены')

    def fill_categories(self):
        if Category.objects.exists():
            print('Категории уже загружены')
            return

        file_path = DATA_DIR + 'category.csv'
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        print('Категории успешно загружены')

    def fill_genres(self):
        if Genre.objects.exists():
            print('Жанры уже загружены')
            return

        file_path = DATA_DIR + 'genre.csv'
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        print('Жанры успешно загружены')

    def fill_titles(self):
        if Title.objects.exists():
            print('Произведения уже загружены')
            return

        file_path = DATA_DIR + 'genre_title.csv'
        mapping = {}
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mapping[row['title_id']] = row['genre_id']

        file_path = DATA_DIR + 'titles.csv'
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Title.objects.create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=Category.objects.get(id=row['category']),
                    genre=Genre.objects.get(id=mapping.get(row['id'], None))
                )
        print('Произведения успешно загружены')

    def fill_reviews(self):
        if Review.objects.exists():
            print('Обзоры уже загружены')
            return

        file_path = DATA_DIR + 'review.csv'
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
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
        if Comments.objects.exists():
            print('Комментарии уже загружены')
            return

        file_path = DATA_DIR + 'comments.csv'
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Comments.objects.create(
                    id=row['id'],
                    review=Review.objects.get(id=row['review_id']),
                    text=row['text'],
                    author=User.objects.get(id=row['author']),
                    pub_date=row['pub_date']
                )
        print('Комментарии успешно загружены')
