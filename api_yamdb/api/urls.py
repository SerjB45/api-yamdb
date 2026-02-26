from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignupAPIView, TokenAPIView, UserMeAPIView, UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', SignupAPIView.as_view(), name='auth_signup'),
    path('v1/auth/token/', TokenAPIView.as_view(), name='auth_token'),
    path('v1/users/me/', UserMeAPIView.as_view(), name='users_me'),
    path('v1/', include(router.urls)),
]
