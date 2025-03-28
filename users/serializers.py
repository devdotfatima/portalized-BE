from rest_framework import serializers
from authentication.models import User
from sports.models import Sport,Position
from django.contrib.auth.hashers import check_password

class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, min_length=6, required=True)

    def validate(self, data):
        user = self.context["request"].user
        if not check_password(data["current_password"], user.password):
            raise serializers.ValidationError({"current_password": "Incorrect password."})
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "mobile_number" ,"email", "username", "full_name", "role", "profile_picture", "first_name", "middle_name", "last_name"]
        ref_name = "UserProfile" 

    def get_full_name(self, obj):
        """Constructs the full name including middle name."""
        return " ".join(filter(None, [obj.first_name, obj.middle_name, obj.last_name]))


class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","mobile_number" ,"profile_picture", "first_name", "middle_name", "last_name"] 



class UserSportPositionSerializer(serializers.ModelSerializer):
    sport = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all(), required=False, allow_null=True)
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "sport", "position"]

    def validate(self, data):
        """
        Ensure the selected position belongs to the selected sport (if both are provided).
        """
        sport = data.get("sport")
        position = data.get("position")

        if position and not sport:
            raise serializers.ValidationError("You must select a sport before choosing a position.")

        if position and sport and position.sport != sport:
            raise serializers.ValidationError("The selected position does not belong to the chosen sport.")

        return data



