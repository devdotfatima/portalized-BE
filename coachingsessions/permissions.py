from rest_framework import generics, permissions
from rest_framework.exceptions import NotAuthenticated


class AuthenticatedBaseView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def check_authenticated(self):
        if getattr(self, 'swagger_fake_view', False):
            return  # Skip authentication check during schema generation
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated("You must be logged in to access this resource.")