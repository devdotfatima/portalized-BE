from django.urls import path
from .views import UserNotificationsView, MarkNotificationsAsReadView

urlpatterns = [
    path('/', UserNotificationsView.as_view(), name='user-notifications'),
    path('/mark-as-read/', MarkNotificationsAsReadView.as_view(), name='mark-notifications-as-read'),
]