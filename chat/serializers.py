from rest_framework import serializers
from .models import Chat
from authentication.models import User


class ChatSerializer(serializers.ModelSerializer):
    participant_1 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    participant_2 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    participant_1_full_name = serializers.SerializerMethodField()
    participant_2_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id',
            'chathead_id',
            'participant_1',
            'participant_2',
            'participant_1_full_name',
            'participant_2_full_name',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_participant_1_full_name(self, obj):
        if obj.participant_1:
            return f"{obj.participant_1.first_name or ''} {obj.participant_1.last_name or ''}".strip()
        return None


    def get_participant_2_full_name(self, obj):
        if obj.participant_2:
            return f"{obj.participant_2.first_name or ''} {obj.participant_2.last_name or ''}".strip()
        return None