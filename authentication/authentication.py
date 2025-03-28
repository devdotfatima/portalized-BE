from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        response = super().authenticate(request)  # ✅ Get user from token
        if response is None:
            return None  # No authentication

        user, token = response
        print(hasattr(user, "last_password_change") and token["iat"] < int(user.last_password_change.timestamp()))
        # 🔹 Ensure token is valid after password reset
        if hasattr(user, "last_password_change") and token["iat"] < int(user.last_password_change.timestamp()):
            raise AuthenticationFailed("Your session has expired. Please log in again.")

        return user, token