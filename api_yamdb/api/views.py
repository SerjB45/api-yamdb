from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import User

from .pagination import UsersPagination
from .permissions import IsAdminRole
from .serializers import (
    SignupSerializer,
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
            from_email=None,
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
