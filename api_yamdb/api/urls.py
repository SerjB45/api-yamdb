from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    SignupAPIView,
    TokenAPIView,
    TitleViewSet,
    UserMeAPIView,
    UserViewSet,
)


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/auth/signup/', SignupAPIView.as_view(), name='auth_signup'),
    path('v1/auth/token/', TokenAPIView.as_view(), name='auth_token'),
    path('v1/users/me/', UserMeAPIView.as_view(), name='users_me'),
    path('v1/', include(router.urls)),
]
