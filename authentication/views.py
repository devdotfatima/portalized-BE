from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .serializers import RegisterSerializer,ResetPasswordSerializer,ForgotPasswordSerializer,AthleteProfileSerializer
from .models import User


def get_access_token_for_user(user):
    """Generate only an access token."""
    return {"access": str(AccessToken.for_user(user))}


class CustomTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Takes user credentials (email & password) and returns an access token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access": openapi.Schema(type=openapi.TYPE_STRING, description="Access Token"),
                },
            ),
            401: "Invalid Credentials",
        },
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            token = get_access_token_for_user(user)
            return Response({"message": "Login successful", "token": token}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: "User registered successfully", 400: "Bad Request"},
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_access_token_for_user(user)
            return Response({"message": "User registered successfully", "tokens": tokens}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """Send password reset link to user's email."""
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"http://127.0.0.1:3000/reset-password/{uid}/{token}/"
            print("jere")
            # Simulating email sending (replace with real email function)
            send_mail(
                "Reset Your Password",
                f"Click the link to reset your password: {reset_link}",
                "noreply@example.com",
                [email],
            )
            return Response({"message": "Password reset link sent!"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    """Verify reset token and change password."""
    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            # Use serializer to validate request data
            serializer = ResetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)



            new_password = serializer.validated_data["password"]
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
            },
            required=["refresh"],
        ),
        responses={200: "Logged out successfully", 400: "Invalid token"},
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")  
            print(refresh_token)
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



class AthleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Complete Athlete Profile",
        operation_description="Allows an authenticated athlete to complete their profile after initial registration.",
        request_body=AthleteProfileSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                examples={"application/json": {"message": "Athlete profile updated successfully"}},
            ),
            400: "Bad Request – Invalid input"
        }
    )
    def put(self, request):
        serializer = AthleteProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Athlete profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)