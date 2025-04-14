from rest_framework import serializers
from .models import Post, Like, Comment

class CommentSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_profile_picture = serializers.CharField(source='user.profile_picture', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user',  'post', 'content', 'created_at',  'user_first_name', 'user_last_name',
            'user_profile_picture']
        read_only_fields = ['id', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'user_email', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()  
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_profile_picture = serializers.CharField(source='user.profile_picture', read_only=True)
    class Meta:
        model = Post
        fields = [
            'id', 'user',  'caption', 'media_urls',
            'created_at', 'likes_count', 'comments_count', 'is_liked_by_user', 
            'post_type', 'location', 'music', 'privacy', 'comments','user_first_name', 'user_last_name',
            'user_profile_picture'
        ]
        read_only_fields = ['id', 'created_at', 'likes_count', 'comments_count']
    
    def get_is_liked_by_user(self, obj):
        request_user = self.context.get('request').user
        return obj.is_liked_by_user(user=request_user)

    def get_comments(self, obj):
        # Only include comments if this is a single post (not part of the list)
        if self.context.get('is_single_post', False):
            return CommentSerializer(obj.comments.all(), many=True).data
        return []

    
