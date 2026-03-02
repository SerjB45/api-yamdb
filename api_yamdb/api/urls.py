from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupAPIView,
    TokenAPIView,
    TitleViewSet,
    UserMeAPIView,
    UserViewSet,
)

list_create = {
    'get': 'list',
    'post': 'create'
}
detail_actions = {
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
}

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
    path('v1/titles/<int:title_id>/reviews/',
         ReviewViewSet.as_view(list_create), name='title_reviews'),
    path('v1/titles/<int:title_id>/reviews/<int:pk>/',
         ReviewViewSet.as_view(detail_actions), name='title_review_detail'),
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/comments/',
         CommentViewSet.as_view(list_create), name='review_comments'),
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
         CommentViewSet.as_view(detail_actions), name='review_comment_detail'),
]
