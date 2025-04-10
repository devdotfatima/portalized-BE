from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "profile_picture"]


    
class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)  

    class Meta:
        model = User
        fields = ["email", "password", "role", "first_name", "middle_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        required=True,  # Ensure this field is mandatory
        error_messages={
            "required": "Password is required.",
            "min_length": "Password must be at least 6 characters long."
        }
    )


    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True) 


class AthleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "dob", "gender", "height", "weight",
            "high_school", "college", "division",
            "school_year", "year_left_to_play",
            "sport", "position","profile_picture"
        ]