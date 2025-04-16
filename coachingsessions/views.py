from rest_framework import  generics
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from authentication.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import AnonymousUser
from .models import SessionRequest
from .serializers import SessionRequestSerializer,InputSessionRequestSerializer
from .permissions import AuthenticatedBaseView



class SessionRequestListView(AuthenticatedBaseView, generics.ListAPIView):
    serializer_class = SessionRequestSerializer

    @swagger_auto_schema(
        operation_description="List all session requests where user is a coach or athlete.",
        responses={200: SessionRequestSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.check_authenticated()
        user = self.request.user
        return SessionRequest.objects.filter(
            models.Q(athlete=user) | models.Q(coach=user)
        )


class SessionRequestDetailView(AuthenticatedBaseView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SessionRequestSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a session request.",
        responses={200: SessionRequestSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a session request.",
        request_body=SessionRequestSerializer,
        responses={200: SessionRequestSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a session request.",
        responses={204: 'No Content'},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return SessionRequest.objects.none()
        return SessionRequest.objects.filter(
            models.Q(athlete=user) | models.Q(coach=user)
        )
    
class SessionRequestCreateView(AuthenticatedBaseView, generics.CreateAPIView):
    serializer_class = SessionRequestSerializer  # for output

    @swagger_auto_schema(
        operation_description="Create a session request. Either athlete or coach can initiate.",
        request_body=InputSessionRequestSerializer,  # for input
        responses={201: SessionRequestSerializer},
    )
    def post(self, request, *args, **kwargs):
        self.check_authenticated()
        user = request.user
        data = request.data.copy()

        coach_id = data.get("coach")
        athlete_id = data.get("athlete")

        if coach_id and not athlete_id:
            data["athlete"] = user.id
        elif athlete_id and not coach_id:
            data["coach"] = user.id
        else:
            return Response(
                {"error": "Must provide either 'coach' or 'athlete', but not both."},
                status=400,
            )

        input_serializer = InputSessionRequestSerializer(data=data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data

        session_request = SessionRequest.objects.create(**validated_data)
        output_serializer = SessionRequestSerializer(session_request)
        return Response(output_serializer.data, status=201)