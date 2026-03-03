from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import exceptions, filters, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import Category, Comment, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import CommonSettingMixin, GenreCategoryMixin
from .pagination import UsersPagination
from .permissions import (
    IsAdminRole,
    IsAuthorOrModeratorOrAdminOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    SignupSerializer,
    TitleSerializer,
    TitleReadSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
    ReviewSerializer,
    CommentSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminRole,)
    pagination_class = UsersPagination
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class SignupAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        data = {
            'email': user.email,
            'username': user.username,
        }
        return Response(data, status=status.HTTP_200_OK)


class TokenAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token = str(AccessToken.for_user(user))
        return Response({'token': token}, status=status.HTTP_200_OK)


class UserMeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserMeSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(
    CommonSettingMixin, GenreCategoryMixin, viewsets.ModelViewSet
):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed("GET")


class GenreViewSet(
    CommonSettingMixin, GenreCategoryMixin, viewsets.ModelViewSet
):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    http_method_names = ('get', 'post', 'delete',)

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed("GET")


class TitleViewSet(CommonSettingMixin, viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all().order_by('name')
    serializer_class = TitleSerializer
    search_fields = ('name', 'genre__slug', 'category__slug', 'year')
    http_method_names = ('get', 'post', 'delete', 'patch',)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly]
    pagination_class = UsersPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id).order_by('-pub_date')

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)

        if Review.objects.filter(
            author=self.request.user,
            title=title
        ).exists():
            raise ValidationError('Вы уже оставили отзыв на это произведение')

        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly]
    pagination_class = UsersPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')

        return Comment.objects.filter(review_id=review_id).order_by(
            'pub_date'
        )

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)
