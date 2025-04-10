from rest_framework import serializers
from .models import SessionRequest

class SessionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionRequest
        fields = '__all__'
        read_only_fields = ['athlete']