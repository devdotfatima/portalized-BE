from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from math import ceil
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Follow
from authentication.models import User
from users.serializers import UserSerializer



# Pagination Class for Follow/Followers
class FollowPagination(PageNumberPagination):
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


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FollowPagination

    @swagger_auto_schema(
        operation_summary="Follow a user",
        operation_description="Allows a logged-in user to follow another user.",
        responses={200: openapi.Response("Successfully followed the user"),
                   400: openapi.Response("Already following or self-following")},
    )
    @action(detail=False, methods=['post'], url_path='follow/(?P<user_id>\d+)')
    def follow_user(self, request, user_id=None):
        if request.user.id == int(user_id):
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        followed_user = get_object_or_404(User, id=user_id)

        # Check if already following
        if Follow.objects.filter(follower=request.user, followed=followed_user).exists():
            return Response({"error": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a follow
        Follow.objects.create(follower=request.user, followed=followed_user)

        return Response({"message": "You are now following this user."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Unfollow a user",
        operation_description="Allows a logged-in user to unfollow another user.",
        responses={200: openapi.Response("Successfully unfollowed the user"),
                   400: openapi.Response("Not following this user")},
    )
    @action(detail=False, methods=['post'], url_path='unfollow/(?P<user_id>\d+)')
    def unfollow_user(self, request, user_id=None):
        followed_user = get_object_or_404(User, id=user_id)

        # Check if following
        follow_instance = Follow.objects.filter(follower=request.user, followed=followed_user).first()
        if not follow_instance:
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

        # Unfollow
        follow_instance.delete()

        return Response({"message": "You have unfollowed this user."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Get Followers List",
        operation_description="Get a paginated list of followers of the logged-in user.",
        responses={200: UserSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='followers')
    def followers_list(self, request):
        followers = Follow.objects.filter(followed=request.user)
        follower_users = [follow.follower for follow in followers]

        # Pagination
        paginator = FollowPagination()
        result_page = paginator.paginate_queryset(follower_users, request)
        serializer = UserSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get Following List",
        operation_description="Get a paginated list of users that the logged-in user is following.",
        responses={200: UserSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='following')
    def following_list(self, request):
        following = Follow.objects.filter(follower=request.user)
        following_users = [follow.followed for follow in following]

        # Pagination
        paginator = FollowPagination()
        result_page = paginator.paginate_queryset(following_users, request)
        serializer = UserSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Check if following a user",
        operation_description="Check if the logged-in user is following a specific user.",
        responses={200: openapi.Response("Is following", openapi.Schema(type=openapi.TYPE_BOOLEAN))},
    )
    @action(detail=False, methods=['get'], url_path='is-following/(?P<user_id>\d+)')
    def is_following(self, request, user_id=None):
        followed_user = get_object_or_404(User, id=user_id)

        # Check if the logged-in user is following the target user
        is_following = Follow.objects.filter(follower=request.user, followed=followed_user).exists()

        return Response({"is_following": is_following}, status=status.HTTP_200_OK)