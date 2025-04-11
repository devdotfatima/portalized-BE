from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from authentication.models import User
from drf_yasg.utils import swagger_auto_schema
from .serializers import UserSerializer, EditProfileSerializer,UpdatePasswordSerializer,FullUserProfileSerializer

class GetUserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can access

    @swagger_auto_schema(responses={200: FullUserProfileSerializer})
    def get(self, request):
        """Retrieve the authenticated user's profile."""
        serializer = FullUserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]  

    @swagger_auto_schema(request_body=UpdatePasswordSerializer)
    def post(self, request):
        """Change password for an authenticated user."""
        serializer = UpdatePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data["new_password"])  # ✅ Update password
            request.user.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditUserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can edit

    @swagger_auto_schema(request_body=EditProfileSerializer, responses={200: "Profile updated successfully"})
    def put(self, request):
        """Edit the authenticated user's profile."""
        serializer = EditProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)