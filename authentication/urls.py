from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import RegisterView, LogoutView, CustomTokenObtainPairView,ResetPasswordView,ForgotPasswordView,AthleteProfileView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"), 
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  
    path("auth/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("auth/password/reset/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/password/reset/<str:uidb64>/<str:token>/", ResetPasswordView.as_view(), name="reset-password"),
     path("auth/athlete/profile/", AthleteProfileView.as_view(), name="athlete-profile"),
]