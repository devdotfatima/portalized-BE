from rest_framework import serializers
from .models import SessionRequest
from authentication.models import User




class UserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_picture']

    def get_full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()



class SessionRequestSerializer(serializers.ModelSerializer):
    athlete = UserMiniSerializer(read_only=True)
    coach = UserMiniSerializer(read_only=True)

    class Meta:
        model = SessionRequest
        fields = '__all__'
        read_only_fields = ['created_at']



class InputSessionRequestSerializer(serializers.ModelSerializer):
    coach = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    athlete = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    class Meta:
        model = SessionRequest
        fields = ['coach', 'athlete', 'session_date', 'session_time', 'notes']