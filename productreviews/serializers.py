from rest_framework import serializers
from .models import Review
from orders.models import OrderItem 


class CreateReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = Review
        fields = ["id", "user", "product", "product_name", "rating", "review_text", "created_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        """Ensure the user has purchased the product before reviewing."""
        user = self.context["request"].user  # Get the authenticated user
        product = validated_data["product"]

        # Find an order where the user has purchased this product
        order_item = OrderItem.objects.filter(order__user=user, product=product).first()

        if not order_item:
            raise serializers.ValidationError("You can only review products you have purchased.")

        # Set the user and order before saving
        validated_data["user"] = user
        validated_data["order"] = order_item.order  # Link the review to the order

        return super().create(validated_data)




class ReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source="user.id")
    user_email = serializers.ReadOnlyField(source="user.email")
    user_first_name = serializers.ReadOnlyField(source="user.first_name")
    user_last_name = serializers.ReadOnlyField(source="user.last_name")
    user_profile_picture = serializers.ReadOnlyField(source="user.profile_picture")
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = Review
        fields = [
            "id",
            "user_id",
            "user_email",
            "user_first_name",
            "user_last_name",
            "user_profile_picture",
            "product",
            "product_name",
            "rating",
            "review_text",
            "created_at",
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        """Ensure the user has purchased the product before reviewing."""
        user = self.context["request"].user  # Get the authenticated user
        product = validated_data["product"]

        # Find an order where the user has purchased this product
        order_item = OrderItem.objects.filter(order__user=user, product=product).first()

        if not order_item:
            raise serializers.ValidationError("You can only review products you have purchased.")

        # Set the user and order before saving
        validated_data["user"] = user
        validated_data["order"] = order_item.order  # Link the review to the order

        return super().create(validated_data)