from django.urls import path
from .views import (
    SessionRequestCreateView,
    SessionRequestListView,
    SessionRequestDetailView,SessionRequestStatusUpdateView
)

urlpatterns = [
    path('/', SessionRequestListView.as_view(), name='session-list'),
    path('/create/', SessionRequestCreateView.as_view(), name='session-create'),
    path('/<int:pk>/', SessionRequestDetailView.as_view(), name='session-detail'),
    path('/<int:session_request_id>/status/', SessionRequestStatusUpdateView.as_view(), name='session-request-status-update'),
]