from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignupAPIView, TokenAPIView, UserMeAPIView, UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', SignupAPIView.as_view(), name='auth_signup'),
    path('auth/token/', TokenAPIView.as_view(), name='auth_token'),
    path('users/me/', UserMeAPIView.as_view(), name='users_me'),
    path('', include(router.urls)),
]
