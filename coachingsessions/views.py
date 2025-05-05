from rest_framework import  generics
from rest_framework.response import Response
from rest_framework import views
from drf_yasg import openapi
from django.db import models
from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import AnonymousUser
from .models import SessionRequest
from .serializers import SessionRequestSerializer,InputSessionRequestSerializer
from .permissions import AuthenticatedBaseView
from math import ceil
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class SessionRequestPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        total_pages = ceil(self.page.paginator.count / self.page_size)
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class SessionRequestStatusUpdateView(AuthenticatedBaseView, views.APIView):

    @swagger_auto_schema(
        operation_description="Accept or Reject a session request (receiver only).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['accepted', 'rejected'],
                    description="Set status to 'accepted' or 'rejected'."
                )
            },
            required=['status']
        ),
        responses={200: 'Success', 400: 'Bad Request', 403: 'Forbidden'},
    )
    def patch(self, request, session_request_id):
        self.check_authenticated()
        user = request.user

        try:
            session_request = SessionRequest.objects.get(id=session_request_id)
        except SessionRequest.DoesNotExist:
            return Response({'error': 'Session request not found.'}, status=404)

        # Only receiver (not initiator) can accept/reject
        if session_request.coach != user and session_request.athlete != user:
            return Response({'error': 'You are not allowed to modify this session request.'}, status=403)

        data = request.data
        new_status = data.get('status')

        if new_status not in ['accepted', 'rejected']:
            return Response({'error': "Status must be 'accepted' or 'rejected'."}, status=400)

        session_request.status = new_status
        session_request.save()

        return Response({'message': f'Session request {new_status} successfully.'}, status=200)


class SessionsBetweenUsersView(AuthenticatedBaseView, generics.ListAPIView):
    serializer_class = SessionRequestSerializer
    pagination_class = SessionRequestPagination

    @swagger_auto_schema(
        operation_description="Get paginated session requests between two users (coach and athlete).",
        manual_parameters=[
            openapi.Parameter('user1_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True, description='First user ID'),
            openapi.Parameter('user2_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True, description='Second user ID'),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page size (max 50)'),
        ],
        responses={200: SessionRequestSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.check_authenticated()

        user1_id = self.request.query_params.get('user1_id')
        user2_id = self.request.query_params.get('user2_id')

        if not user1_id or not user2_id:
            return SessionRequest.objects.none()

        return SessionRequest.objects.filter(
            (Q(coach_id=user1_id) & Q(athlete_id=user2_id)) |
            (Q(coach_id=user2_id) & Q(athlete_id=user1_id))
        ).order_by('-session_date', '-session_time')


class SessionRequestListView(AuthenticatedBaseView, generics.ListAPIView):
    serializer_class = SessionRequestSerializer
    pagination_class = SessionRequestPagination

    @swagger_auto_schema(
        operation_summary="List session requests",
        operation_description="""
        - Filter by status (`pending`, `accepted`, `rejected`).
        - Filter dynamically by time (`upcoming`, `completed`).
        - Supports pagination (`page`, `page_size`).
        """,
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING),
            openapi.Parameter('type', openapi.IN_QUERY, description="Filter by type (upcoming, completed)", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page size'),
        ],
        responses={200: SessionRequestSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.check_authenticated()
        user = self.request.user
        queryset = SessionRequest.objects.filter(
            models.Q(athlete=user) | models.Q(coach=user)
        ).order_by('-session_date', '-session_time')

        status_filter = self.request.query_params.get('status')
        type_filter = self.request.query_params.get('type')

        now = timezone.now()

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if type_filter:
              if type_filter == 'upcoming':
                  queryset = queryset.filter(
                      models.Q(status='accepted') & (
                          models.Q(session_date__gt=now.date()) |
                          models.Q(session_date=now.date(), session_time__gte=now.time())
                      )
                  )
              elif type_filter == 'completed':
                  queryset = queryset.filter(
                      models.Q(status='accepted') & (
                          models.Q(session_date__lt=now.date()) |
                          models.Q(session_date=now.date(), session_time__lt=now.time())
                      )
                  )

        return queryset


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