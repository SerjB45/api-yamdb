from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueValidator

from api.validators import validate_username_not_me
from reviews.core import MAX_SCORE, MIN_SCORE
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title
)

User = get_user_model()

USERNAME_REGEX = r'^[\w.@+-]+\Z'


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=150,
        validators=[validate_username_not_me],
    )

    def validate(self, attrs):
        username = attrs['username']
        email = attrs['email']

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError(
                {'username': ['Пользователь с таким username уже существует.']}
            )
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError(
                {'email': ['Пользователь с таким email уже существует.']}
            )

        return attrs

    def save(self, **kwargs):
        email = self.validated_data['email']
        username = self.validated_data['username']
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=150,
    )
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        username = attrs['username']
        confirmation_code = attrs['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as error:
            raise NotFound('Пользователь не найден.') from error

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': ['Неверный код подтверждения.']}
            )

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=150,
        validators=[
            validate_username_not_me,
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserMeSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(
        read_only=True,
    )
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )
        read_only_fields = ('id', 'author', 'pub_date')

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            title = self.context['view'].kwargs.get('title_id')
            author = self.context['request'].user
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data

    def validate_score(self, value):
        if value < MIN_SCORE or value > MAX_SCORE:
            raise serializers.ValidationError(
                'Оценка должна быть целым числом от 1 до 10.'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
        read_only_fields = ('id', 'author', 'pub_date')
