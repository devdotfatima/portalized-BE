from rest_framework import serializers
from .models import Post, Like, Comment

class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_email', 'post', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'user_email', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'user_email', 'caption', 'media_urls',
            'created_at', 'likes_count', 'comments_count', 'comments'
        ]
        read_only_fields = ['id', 'created_at', 'likes_count', 'comments_count', 'comments']