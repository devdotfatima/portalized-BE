from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer

class GetCartView(APIView):
    """Retrieve the authenticated user's cart."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get User Cart",
        operation_description="Retrieve the authenticated user's cart along with all added products.",
        responses={200: CartSerializer}
    )
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    """Add a product to the cart or update quantity."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Add Product to Cart",
        operation_description="Add a product to the user's cart or update its quantity if already added.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["product_id", "quantity"],
            properties={
                "product_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the product"),
                "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, description="Quantity of the product"),
            },
        ),
        responses={200: "Product added to cart", 404: "Product not found"}
    )
    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        print(quantity)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            cart_item.quantity = quantity  # ✅ Set quantity only if item is new
        else:
            cart_item.quantity += quantity  # ✅ Otherwise, increase quantity

    
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    """Update the quantity of a cart item. If quantity is 0, delete the item."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update Cart Item Quantity",
        operation_description="Update the quantity of a product in the cart. If quantity is set to 0, the item is removed.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["quantity"],
            properties={
                "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, description="New quantity of the product"),
            },
        ),
        responses={200: "Cart updated successfully", 404: "Cart item not found"}
    )
    def put(self, request, item_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)  # Ensure cart exists
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        quantity = int(request.data.get("quantity", 1))

        if quantity <= 0:
            cart_item.delete()  # ✅ Remove item if quantity is zero
        else:
            cart_item.quantity = quantity
            cart_item.save()

        # ✅ Return updated cart items
        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        print(serializer.data) 
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteCartItemView(APIView):
    """Remove a specific cart item and return updated cart items."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Remove Item from Cart",
        operation_description="Remove a specific item from the authenticated user's cart and return the updated cart items.",
        responses={200: "Item removed successfully", 404: "Cart item not found"}
    )
    def delete(self, request, item_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Return updated cart items
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClearCartView(APIView):
    """Remove all items from the cart."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Clear Cart",
        operation_description="Remove all items from the authenticated user's cart.",
        responses={200: "Cart cleared successfully"}
    )
    def delete(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared successfully"}, status=status.HTTP_200_OK)