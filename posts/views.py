from rest_framework.response import Response
from django.contrib.auth.models import AnonymousUser
from math import ceil
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from rest_framework import filters


class CommentPagination(PageNumberPagination):
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


class PostPagination(PageNumberPagination):
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


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post_type', 'user']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
        # Return an empty queryset or some safe fallback
          return Post.objects.none()
        queryset = Post.objects.prefetch_related('likes', 'comments').order_by('-created_at')
        
            # Filter by user if provided
        user_param = self.request.query_params.get('user')
        if user_param:
            queryset = queryset.filter(user_id=user_param)
        else:
            # Only exclude current user's posts if no specific user is requested
            if not isinstance(self.request.user, AnonymousUser):
                queryset = queryset.exclude(user=self.request.user)
        return queryset

    @swagger_auto_schema(
        operation_summary="List posts (feed)",
        operation_description="""
        Returns a list of posts for the feed.
        - Excludes current user's own posts unless filtered by `user`.
        - Optional filters:
            - `user`: ID of the user to get posts for.
            - `post_type`: Filter by media type (`text`, `image`, `reel`)
            - Pagination supported with `page` and `page_size`.
        """,
        manual_parameters=[
            openapi.Parameter('user', openapi.IN_QUERY, description="User ID to filter posts", type=openapi.TYPE_INTEGER),
            openapi.Parameter('post_type', openapi.IN_QUERY, description="Filter by media type: text/image/reel", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page size'),
        ],
        responses={200: PostSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        posts_with_likes = []
        for post in serializer.data:
            post['is_liked'] = Post.objects.get(id=post['id']).is_liked_by_user(user=request.user)
            posts_with_likes.append(post)

        return self.get_paginated_response(posts_with_likes)

    @swagger_auto_schema(
        operation_summary="Retrieve a single post",
        operation_description="Returns a specific post by ID.",
        responses={200: PostSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer.context['is_single_post'] = True
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a post",
        operation_description="Creates a new post for the logged-in user.",
        request_body=PostSerializer,
        responses={201: PostSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get paginated comments for a post",
        operation_description="Returns paginated comments on a specific post by post ID.",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Comments per page'),
        ],
        responses={200: CommentSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='comments')
    def paginated_comments(self, request, pk=None):
        post = self.get_object()
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        paginator = CommentPagination()
        result_page = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Toggle like/unlike",
        operation_description="""
        Likes a post if not already liked by the user, otherwise unlikes it.
        Request body must include:
        - `post`: Post ID
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['post'],
            properties={
                'post': openapi.Schema(type=openapi.TYPE_INTEGER, description='Post ID to like/unlike'),
            },
        ),
        responses={
            200: openapi.Response("Unliked", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            })),
            201: LikeSerializer(),
            400: openapi.Response("Bad request"),
            404: openapi.Response("Post not found")
        }
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        post_id = request.data.get("post")

        if not post_id:
            return Response({"error": "post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Post not found.")

        existing_like = Like.objects.filter(user=user, post=post).first()

        if existing_like:
            existing_like.delete()
            return Response({"message": "Post unliked"}, status=status.HTTP_200_OK)
        else:
            like = Like.objects.create(user=user, post=post)
            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a comment",
        operation_description="Creates a comment on a post for the logged-in user.",
        request_body=CommentSerializer,
        responses={201: CommentSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List all comments",
        operation_description="Lists all comments with pagination.",
        responses={200: CommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a single comment",
        operation_description="Retrieve a specific comment by its ID.",
        responses={200: CommentSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)