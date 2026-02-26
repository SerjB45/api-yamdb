from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueValidator

User = get_user_model()

USERNAME_REGEX = r'^[\w.@+-]+\Z'
RESERVED_USERNAME_ERROR = 'Использовать имя "me" запрещено.'


def validate_username_not_me(value):
    if value.lower() == 'me':
        raise serializers.ValidationError(RESERVED_USERNAME_ERROR)
    return value


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
