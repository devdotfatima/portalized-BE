from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer

class CommentPagination(PageNumberPagination):
    page_size = 10  # Default comments per page
    page_size_query_param = 'page_size'
    max_page_size = 50

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        posts_with_likes = []
        for post in serializer.data:
            post['is_liked'] = Post.objects.get(id=post['id']).is_liked_by_user(user=request.user)
            posts_with_likes.append(post)
        return Response(posts_with_likes)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer.context['is_single_post'] = True
        return Response(serializer.data)

    def get_queryset(self):
        return Post.objects.prefetch_related('likes').all()

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)