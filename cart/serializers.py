from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")  # ✅ Show product name in response
    product_image = serializers.SerializerMethodField()  # ✅ Get first image

    class Meta:
        model = CartItem
        fields = ["id","price_at_purchase" ,"product", "product_name", "product_image", "quantity"]

    def get_product_image(self, obj):
        """Return the first image from the product images array."""
        if isinstance(obj.product.images, list) and obj.product.images:
            return obj.product.images[0]  # ✅ Return first image
        return None  # ✅ Return None if no images are available

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]