from django.urls import path
from .views import GetUserProfileView, EditUserProfileView,UpdatePasswordView

urlpatterns = [
    path("profile/", GetUserProfileView.as_view(), name="get-profile"),  
    path("profile/edit/", EditUserProfileView.as_view(), name="edit-profile"),  
    path("profile/update-password/", UpdatePasswordView.as_view(), name="update-password"),
]