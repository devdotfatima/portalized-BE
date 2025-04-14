from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Override the list method to add "is_liked" field in response
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Add "is_liked" to each post
        posts_with_likes = []
        for post in serializer.data:
            post['is_liked'] = Post.objects.get(id=post['id']).is_liked_by_user(user=request.user)
            posts_with_likes.append(post)

        return Response(posts_with_likes)

    # Override the retrieve method to include comments for a single post
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Set context variable to include comments for single post
        serializer.context['is_single_post'] = True
        return Response(serializer.data)

    # Don't include comments in the response for the list of posts
    def get_queryset(self):
        return Post.objects.prefetch_related('likes').all()


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