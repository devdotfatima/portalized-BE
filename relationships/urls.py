from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FollowViewSet

# Initialize the router
router = DefaultRouter()
router.register(r'', FollowViewSet, basename='follow')

# Define your URL patterns
urlpatterns = [
    path('', include(router.urls)),  # All Follow-related URLs
]