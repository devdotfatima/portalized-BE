from rest_framework import  generics
from django.db import models
from django.contrib.auth.models import AnonymousUser
from .models import SessionRequest
from .serializers import SessionRequestSerializer
from .permissions import AuthenticatedBaseView

class SessionRequestCreateView(AuthenticatedBaseView, generics.CreateAPIView):
    serializer_class = SessionRequestSerializer

    def perform_create(self, serializer):
        self.check_authenticated()  # Optional, based on the view
        serializer.save(athlete=self.request.user)


class SessionRequestListView(AuthenticatedBaseView, generics.ListAPIView):
    serializer_class = SessionRequestSerializer

    def get_queryset(self):
        self.check_authenticated()
        return SessionRequest.objects.filter(coach=self.request.user)


class SessionRequestDetailView(AuthenticatedBaseView, generics.RetrieveUpdateDestroyAPIView):
    queryset = SessionRequest.objects.all()
    serializer_class = SessionRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            # Handle the case where the user is not authenticated
            return SessionRequest.objects.none()  # Or any other appropriate action
        return SessionRequest.objects.filter(
            models.Q(athlete=user) | models.Q(coach=user)
        )