from rest_framework import serializers
from authentication.models import User
from .models import Order, OrderItem,ShippingAddress


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "product_image", "quantity", "price_at_purchase"]

    def get_product_image(self, obj):
        """Return the first image of the product if available."""
        return obj.product.images[0] if obj.product.images else None


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        exclude = ["order"]  # Exclude order from request data, it will be added later

    def validate(self, data):
        """Ensure all required fields are present."""
        required_keys = {"street_address", "city", "state", "zip_code", "country", "first_name", "last_name", "phone_number"}
        missing_keys = required_keys - data.keys()

        if missing_keys:
            raise serializers.ValidationError(f"Missing required fields: {', '.join(missing_keys)}")

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]

class OrderSerializer(serializers.ModelSerializer):
    shipping_address = ShippingAddressSerializer()
    items = OrderItemSerializer(many=True, read_only=True,)
    user = UserSerializer(read_only=True)  

    class Meta:
        model = Order
        fields = ["id", "user", "total_price", "status", "created_at", "shipping_address","items"]
        read_only_fields = ["id", "created_at", "user"]

