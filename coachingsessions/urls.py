from django.urls import path
from .views import (
    SessionRequestCreateView,
    SessionRequestListView,
    SessionRequestDetailView
)

urlpatterns = [
    path('/', SessionRequestListView.as_view(), name='session-list'),
    path('/create/', SessionRequestCreateView.as_view(), name='session-create'),
    path('/<int:pk>/', SessionRequestDetailView.as_view(), name='session-detail'),
]