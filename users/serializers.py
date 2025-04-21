from rest_framework import serializers
from authentication.models import User
from sports.models import Sport,Position
from django.contrib.auth.hashers import check_password


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ["id", "name"]
        ref_name = "UserSport"  # Add this

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ["id", "name"]
        ref_name = "UserPosition"  # Add this


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
        fields = ["username","mobile_number" ,"profile_picture", "first_name", "middle_name", "last_name",  "fcm_token",
            "is_online",
            "notify_on_like",
            "notify_on_comment",
            "notify_on_chat"] 



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



class FullUserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    sport = SportSerializer(read_only=True)
    position = PositionSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "full_name", "role", "mobile_number", "profile_picture",
            "first_name", "middle_name", "last_name",
            "dob", "gender",
            "height", "height_unit",
            "weight", "weight_unit",
            "high_school", "college", "division", "school_year", "year_left_to_play",
            "sport", "position",
            "fcm_token","performance_statistics","fcm_token",
            "is_online",
            "notify_on_like",
            "notify_on_comment",
            "notify_on_chat"
        ]

    def get_full_name(self, obj):
        return " ".join(filter(None, [obj.first_name, obj.middle_name, obj.last_name]))