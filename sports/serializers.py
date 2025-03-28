from rest_framework import serializers
from .models import Sport, Position

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ["id", "sport", "name"]

class SportSerializer(serializers.ModelSerializer):
    positions = PositionSerializer(many=True, read_only=True)  # Nested serializer to show positions in a sport

    class Meta:
        model = Sport
        fields = ["id", "name", "created_at", "positions"]
        read_only_fields = [ "created_at"]  # Prevent users from modifying these fields