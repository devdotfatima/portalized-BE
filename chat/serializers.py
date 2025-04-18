from rest_framework import serializers
from authentication.models import User
from .models import Chat

class UserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        ref_name = "ChatUserMiniSerializer"  
        fields = ["id", "email", "first_name", "last_name", "profile_picture", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
    

class ChatSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    participant_details = UserMiniSerializer(source='participants', many=True, read_only=True)

    class Meta:
        model = Chat
        fields = [
            'id',
            'chathead_id',
            'participants',
            'participant_details',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        participants = data.get('participants', [])
        if len(participants) != 2:
            raise serializers.ValidationError("Chat must have exactly 2 participants.")

        user_ids = sorted([user.id for user in participants])
        existing_chat = Chat.objects.filter(participants__id=user_ids[0]) \
                                    .filter(participants__id=user_ids[1]) \
                                    .distinct()
        for chat in existing_chat:
            if chat.participants.count() == 2:
                raise serializers.ValidationError("A chat between these two users already exists.")

        return data

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if self.context['request'].method == 'GET':
            rep.pop('participants', None)
        return rep