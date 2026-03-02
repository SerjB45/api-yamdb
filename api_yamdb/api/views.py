from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, User
from .pagination import UsersPagination
from .permissions import (
    IsAdminOrReadyOnly,
    IsAdminRole,
    IsAuthorModeratorAdminOrReadOnly,
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
            from_email=settings.DEFAULT_FROM_EMAIL,
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
    viewsets.ModelViewSet
):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    http_method_names = ('get', 'post', 'delete',)
    permission_classes = (IsAdminOrReadyOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed("GET")


class GenreViewSet(
    viewsets.ModelViewSet
):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer

    http_method_names = ('get', 'post', 'delete',)
    permission_classes = (IsAdminOrReadyOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed("GET")


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().order_by('name')
    serializer_class = TitleSerializer

    permission_classes = (IsAdminOrReadyOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'genre__slug', 'category__slug', 'year')

    http_method_names = ('get', 'post', 'delete', 'patch',)

    def get_queryset(self):
        queryset = super().get_queryset()

        params = {
            'genre__slug': self.request.query_params.get('genre'),
            'category__slug': self.request.query_params.get('category'),
            'year': self.request.query_params.get('year'),
            'name__icontains': self.request.query_params.get('name'),
        }

        filtered_params = {k: v for k, v in params.items() if v}
        if filtered_params:
            queryset = queryset.filter(**filtered_params)

        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleSerializer
