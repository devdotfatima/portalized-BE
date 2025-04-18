from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from math import ceil
from rest_framework.response import Response
from datetime import date
from django.db.models import Q
from rest_framework.generics import ListAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from authentication.models import User
from drf_yasg.utils import swagger_auto_schema
from .serializers import UserSerializer, EditProfileSerializer,UpdatePasswordSerializer,FullUserProfileSerializer

class GetUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user', openapi.IN_QUERY, description="User ID to fetch profile for (optional)", type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: FullUserProfileSerializer}
    )
    def get(self, request):
        user_id = request.query_params.get("user")

        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user

        serializer = FullUserProfileSerializer(user)
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
    
class AthleteSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        total_pages = ceil(self.page.paginator.count / self.page.paginator.per_page)
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class AthleteSearchAPIView(ListAPIView):
    serializer_class = FullUserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AthleteSearchPagination
    @swagger_auto_schema(
        operation_summary="Search Users by Role",
        operation_description=(
            "Allows searching for users by role (athlete or coach). "
            "When role=athlete, you can filter by name, weight, height, sport, position, division, and eligibility. "
            "When role=coach, you can only filter by name."
        ),
        manual_parameters=[
            openapi.Parameter("role", openapi.IN_QUERY, description="Role to search: 'athlete' or 'coach'", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("name", openapi.IN_QUERY, description="Search by first, middle, or last name", type=openapi.TYPE_STRING),
            openapi.Parameter("weight", openapi.IN_QUERY, description="Exact weight (athlete only)", type=openapi.TYPE_INTEGER),
            openapi.Parameter("height", openapi.IN_QUERY, description="Exact height (athlete only)", type=openapi.TYPE_INTEGER),
            openapi.Parameter("sport", openapi.IN_QUERY, description="Sport ID (athlete only)", type=openapi.TYPE_INTEGER),
            openapi.Parameter("position", openapi.IN_QUERY, description="Position ID (athlete only)", type=openapi.TYPE_INTEGER),
            openapi.Parameter("division", openapi.IN_QUERY, description="Partial match on division (athlete only)", type=openapi.TYPE_STRING),
            openapi.Parameter("eligibility", openapi.IN_QUERY, description="Years left to play (athlete only)", type=openapi.TYPE_INTEGER),
        ],
        responses={200: FullUserProfileSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
      params = self.request.query_params
      role = params.get("role")

      if role not in ["athlete", "coach"]:
          return User.objects.none()

      queryset = User.objects.filter(role=role)

      # Filters shared for both roles
      name = params.get("name")
      if name:
          queryset = queryset.filter(
              Q(first_name__icontains=name) |
              Q(middle_name__icontains=name) |
              Q(last_name__icontains=name)
          )

      # Extra filters only for athlete role
      if role == "athlete":
          weight = params.get("weight")
          height = params.get("height")
          sport = params.get("sport")
          position = params.get("position")
          division = params.get("division")
          eligibility = params.get("eligibility")

          if weight:
              queryset = queryset.filter(weight=weight)
          if height:
              queryset = queryset.filter(height=height)
          if sport:
              queryset = queryset.filter(sport_id=sport)
          if position:
              queryset = queryset.filter(position_id=position)
          if division:
              queryset = queryset.filter(division__icontains=division)
          if eligibility:
              try:
                  years_left = int(eligibility)
                  cutoff_date = date.today().replace(year=date.today().year + years_left)
                  queryset = queryset.filter(year_left_to_play__lte=cutoff_date)
              except ValueError:
                  pass

      return queryset.order_by("id")