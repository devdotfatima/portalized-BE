from rest_framework import serializers
from .models import Podcast, PodcastLike, PodcastComment

class PodcastSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source="uploaded_by.email")
    total_likes = serializers.SerializerMethodField()
    total_dislikes = serializers.SerializerMethodField()

    class Meta:
        model = Podcast
        fields = "__all__"

    def get_total_likes(self, obj):
        return obj.likes.filter(is_liked=True).count()

    def get_total_dislikes(self, obj):
        return obj.likes.filter(is_liked=False).count()


class PodcastLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastLike
        fields = ["user", "podcast", "is_liked"] 




class PodcastCommentSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source="user.id")
    user_full_name = serializers.SerializerMethodField()
    user_profile_picture = serializers.ReadOnlyField(source="user.profile_picture")

    class Meta:
        model = PodcastComment
        fields = ["id", "user_id", "user_full_name", "user_profile_picture", "podcast", "content", "created_at"]

    def get_user_full_name(self, obj):
        """Returns the full name of the user, falling back to the email if no name is set."""
        full_name = f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip()
        return full_name if full_name else obj.user.email