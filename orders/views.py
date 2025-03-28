from rest_framework.views import APIView
from django.views import View
from rest_framework.permissions import BasePermission
from django.db import transaction
from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,BasePermission
from django.core.mail import send_mail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import stripe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Order, OrderItem, ShippingAddress
from products.models import Product
from cart.models import Cart, CartItem
from .serializers import OrderSerializer


class GetUserOrdersView(APIView):
    """Retrieve a list of user's orders."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get User Orders",
        operation_description="Fetch all orders of the authenticated user.",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IsAdminUser(BasePermission):
    """Custom permission to allow only admins."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "superadmin"


class AdminManageOrderView(APIView):
    """Admins can update order status, update stock, and notify users."""
    permission_classes = [ IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Update Order Status (Admin)",
        operation_description="Admins can update order status (pending, processing, shipped, delivered, cancelled).",
        responses={200: "Order updated successfully", 404: "Order not found"},
    )
    def put(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.data.get("status")

            if new_status not in dict(Order.STATUS_CHOICES):
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ When order is approved, update stock
            if new_status == "cancelled" and order.status in ["pending", "processing"]:
              for item in order.items.all():
                  item.product.stock += item.quantity
                  item.product.save()

            order.status = new_status
            order.save()

            # ✅ Send an email notification on shipped or delivered status
            if new_status in ["cancelled","shipped", "delivered"]:
                self.send_order_update_email(order)

            return Response(
                {"message": "Order updated successfully", "status": order.status},
                status=status.HTTP_200_OK
            )

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    def send_order_update_email(self, order):
        """Send an email notification when order is cancelled, shipped, or delivered."""
        subject = f"Order #{order.id} Update"

        if order.status == "cancelled":
              message = (
                  f"Dear {order.user.first_name},\n\n"
                  f"We regret to inform you that your order #{order.id} has been cancelled.\n"
                  f"If you have any questions, please contact support."
              )
        else:
              message = (
                  f"Dear {order.user.first_name},\n\n"
                  f"Your order #{order.id} status has been updated to {order.status}."
              )

        send_mail(
              subject,
              message,
              settings.EMAIL_HOST_USER,
              [order.user.email],
          )


class GetOrderDetailView(APIView):
    """Retrieve details of a specific order."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get Order Details",
        operation_description="Fetch details of a specific order by ID.",
        responses={200: OrderSerializer, 404: "Order not found"}
    )
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        

class CreatePaymentIntentView(APIView):
    """Create a Stripe Payment Intent."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create Stripe Payment Intent",
        operation_description="Generate a Stripe Payment Intent for order checkout.",
        responses={200: "Payment Intent Created", 400: "Invalid Request"},
    )
    def post(self, request):
        try:
            order_id = request.data.get("order_id")  # ✅ Get order ID from request
            if not order_id:
                return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.filter(id=order_id, user=request.user).first()
            if not order:
                return Response({"error": "Order not found"}, status=status.HTTP_400_BAD_REQUEST)

            amount = order.total_price
            if amount <= 0:
                return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

            stripe.api_key = settings.STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="usd",
                metadata={"order_id": str(order.id)},
            )

            return Response({"client_secret": payment_intent["client_secret"]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

def send_order_confirmation_email(user_email, order_id):
    """Send an email notification when an order is placed."""
    subject = "Order Confirmation"
    message = f"Your order #{order_id} has been placed successfully! We will update you once it's shipped."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])


class PlaceOrderView(APIView):
    """Place an order and send confirmation email."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Place an Order",
        operation_description="Place an order based on the user's cart items. Deducts stock and sends a confirmation email.",
        request_body=OrderSerializer,
        responses={
            201: openapi.Response("Order placed successfully", openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Order placed successfully"),
                    "order_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=123),
                },
            )),
            400: "Bad request",
        },
    )

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).prefetch_related("items__product").first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        shipping_address_data = serializer.validated_data.pop("shipping_address")
        cart_items = cart.items.all()

        # ✅ Check stock before placing order
        insufficient_stock = [
            item.product.name for item in cart_items if item.product.stock < item.quantity
        ]
        if insufficient_stock:
            return Response(
                {"error": f"Insufficient stock for {', '.join(insufficient_stock)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        with transaction.atomic():  # ✅ Ensure atomicity
            order = Order.objects.create(user=request.user, total_price=total_price, status="pending")

            # ✅ Bulk create order items
            order_items = [
                OrderItem(order=order, product=item.product, quantity=item.quantity, price_at_purchase=item.product.price)
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            # ✅ Bulk update stock (only after successful payment)
            
            # ✅ Create shipping address
            ShippingAddress.objects.create(order=order, **shipping_address_data)

            send_order_confirmation_email(request.user.email, order.id)

        return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)


stripe.api_key = settings.STRIPE_SECRET_KEY

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """Handles Stripe Webhook Events"""

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  
       
        
        # 🔍 Debugging logs
        print(f"🔹 STRIPE_WEBHOOK_SECRET: {endpoint_secret}")
        print(f"🔹 Received Stripe Signature: {sig_header}")
        print(f"🔹 Raw Payload: {payload}")

        if not sig_header or not endpoint_secret:
            return JsonResponse({"error": "Webhook secret or signature missing"}, status=400)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            print(f"✅ Stripe Event Parsed: {event['type']}")
        except ValueError:
            print("❌ Invalid Payload")
            return JsonResponse({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            print("❌ Invalid Signature")
            return JsonResponse({"error": "Invalid signature"}, status=400)

        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            order_id = payment_intent.get("metadata", {}).get("order_id")
            
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = "processing"
                    order.payment_status = "succeeded"
                    order.payment_method = payment_intent.get("payment_method_types", [None])[0]  # e.g., 'card'
                    order.payment_id = payment_intent.get("id")
                    order.transaction_reference = payment_intent.get("charges", {}).get("data", [{}])[0].get("id")
                    order.receipt_url = payment_intent.get("charges", {}).get("data", [{}])[0].get("receipt_url")
                    order.save()

                    # ✅ Bulk update stock (only after successful payment)
                    products_to_update = []
                    for item in order.items.select_related("product").all():  # Optimized query
                          product = item.product
                          if product.stock >= item.quantity:
                              product.stock -= item.quantity
                              products_to_update.append(product)
                          else:
                              print(f"⚠️ Not enough stock for {product.name}!")

                      # ✅ Perform bulk update in a single query
                    if products_to_update:
                          Product.objects.bulk_update(products_to_update, ["stock"])


                    # ✅ Remove items from the user's cart (NOW that payment is successful)
                    CartItem.objects.filter(cart__user=order.user).delete()
                    print(f"✅ Order {order_id} updated successfully and cart cleared!")
                except Order.DoesNotExist:
                    print(f"❌ Order {order_id} not found!")

        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            order_id = payment_intent.get("metadata", {}).get("order_id")

            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = "cancelled"
                    order.payment_status = "failed"
                    order.save()
                    print(f"✅ Order {order_id} marked as failed")
                except Order.DoesNotExist:
                    print(f"❌ Order {order_id} not found!")

        return JsonResponse({"status": "success"}, status=200)



class OrderPagination(PageNumberPagination):
    """Custom pagination for orders."""
    page_size = 10  # ✅ Default: 10 orders per page
    page_size_query_param = "page_size"  # ✅ Allows client to specify page size
    max_page_size = 50  # ✅ Prevents excessive data loads


class GetAllOrdersView(generics.ListAPIView):
    """Retrieve all orders with filtering, sorting, and pagination (Admin only)."""
    
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = OrderPagination  # ✅ Enables pagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    # ✅ Filtering options
    filterset_fields = {
        "status": ["exact"],  # Filter by order status (pending, processing, etc.)
        "user__email": ["exact"],  # Filter by user email
        "created_at": ["exact", "lt", "gt"],  # Filter by creation date
        "total_price": ["exact", "lt", "gt"],  # Filter by order price
    }

    # ✅ Search orders by user email
    search_fields = ["user__email"]

    # ✅ Sorting options
    ordering_fields = ["created_at", "total_price", "status"]
    ordering = ["-created_at"]  # Default sorting: newest first

    @swagger_auto_schema(
        operation_summary="Get All Orders (Admin)",
        operation_description=(
            "Retrieve a paginated list of all orders with optional filtering, searching, and sorting."
            "\n\n✅ **Features:**"
            "\n- 🔍 **Search**: Search orders by user email."
            "\n- 🔢 **Filtering**: Filter by status, total price, user email, or creation date."
            "\n- 📊 **Sorting**: Sort by date, total price, or status."
            "\n- 📄 **Pagination**: Default page size is 10 (configurable)."
        ),
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="🔍 Search for orders by user email.",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="🛒 Filter orders by status (`pending`, `processing`, `shipped`, `delivered`, `cancelled`).",
                type=openapi.TYPE_STRING,
                enum=["pending", "processing", "shipped", "delivered", "cancelled"],
            ),
            openapi.Parameter(
                "total_price__lt",
                openapi.IN_QUERY,
                description="💰 Show orders with total price **less than** this value.",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "total_price__gt",
                openapi.IN_QUERY,
                description="💰 Show orders with total price **greater than** this value.",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "created_at__lt",
                openapi.IN_QUERY,
                description="📅 Show orders **before** this date (format: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "created_at__gt",
                openapi.IN_QUERY,
                description="📅 Show orders **after** this date (format: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="📊 Sort orders by `created_at`, `total_price`, or `status` (prefix with `-` for descending).",
                type=openapi.TYPE_STRING,
                enum=["created_at", "-created_at", "total_price", "-total_price", "status", "-status"],
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="📄 Page number for pagination.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="📄 Number of orders per page (default: 10, max: 50).",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: OrderSerializer(many=True),
            400: "Bad request",
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a list of orders with filters, sorting, and pagination."""
        return super().get(request, *args, **kwargs)
    

