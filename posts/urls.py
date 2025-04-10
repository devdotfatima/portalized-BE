from rest_framework.routers import DefaultRouter
from .views import PostViewSet, LikeViewSet, CommentViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'', PostViewSet, basename='post')
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]