from rest_framework import generics, permissions, filters
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Product
from .serializers import ProductSerializer

class IsAdminUser(permissions.BasePermission):
    """Custom permission to allow only admins."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "superadmin"



class CheckProductNameView(APIView):
    """Check if a product with the given name already exists."""

    @swagger_auto_schema(
        operation_summary="Check Product Name Availability",
        operation_description="Checks if a product with the given name already exists.",
        manual_parameters=[
            openapi.Parameter(
                "name", 
                openapi.IN_QUERY, 
                description="Product name to check.", 
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(description="Returns `{ 'exists': true }` if product name exists, otherwise `{ 'exists': false }`.")
        },
    )
    def get(self, request):
        """Handle GET request for checking product name availability."""
        name = request.GET.get("name", "").strip()
        exists = Product.objects.filter(name=name).exists()
        return Response({"exists": exists})


# ✅ Create Product (Admin Only)
class CreateProductView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


class ListProductsView(generics.ListAPIView):
    """List, search, filter, sort, and paginate products."""
    
    queryset = Product.objects.annotate(
        average_rating=Avg("reviews__rating"),  # ✅ Precompute average rating
        total_reviews=Count("reviews")  # ✅ Precompute total reviews
    )
    serializer_class = ProductSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # ✅ Filtering options
    filterset_fields = {
        "price": ["exact", "lt", "gt"],  # Exact, Less Than, Greater Than
        "stock": ["exact", "lt", "gt"],  # Exact, Low Stock, High Stock
    }

    search_fields = ["name"]

    ordering_fields = ["name", "price", "stock", "created_at"]
    ordering = ["-created_at"]  

    @swagger_auto_schema(
        operation_summary="List Products",
        operation_description=(
            "Retrieve a paginated list of products with optional filtering, searching, and sorting."
            "\n\n✅ **Features:**"
            "\n- 🔍 **Search**: Search for products by name."
            "\n- 🔢 **Filtering**: Filter products by price (`exact`, `lt`, `gt`) and stock (`exact`, `lt`, `gt`)."
            "\n- 📊 **Sorting**: Sort by name, price, or stock in ascending/descending order."
            "\n- 📄 **Pagination**: Default page size is set in settings."
        ),
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="🔍 Search for products by name.",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "price__lt",
                openapi.IN_QUERY,
                description="💰 Show products with price **less than** this value.",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "price__gt",
                openapi.IN_QUERY,
                description="💰 Show products with price **greater than** this value.",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "stock__lt",
                openapi.IN_QUERY,
                description="📦 Show products with stock **less than** this value.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "stock__gt",
                openapi.IN_QUERY,
                description="📦 Show products with stock **greater than** this value.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="📊 Sort products by `name`, `price`, or `stock` (prefix with `-` for descending).",
                type=openapi.TYPE_STRING,
                enum=["name", "-name", "price", "-price", "stock", "-stock"],
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="📄 Page number for pagination.",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: ProductSerializer(many=True),
            400: "Bad request",
        },
    )

    def get(self, request, *args, **kwargs):
        """Retrieve a list of products with filters, sorting, and pagination."""
        return super().get(request, *args, **kwargs)


# ✅ Retrieve Single Product by ID (Anyone Can View)
class RetrieveProductView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Public access


# ✅ Update Product (Admin Only)
class UpdateProductView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


# ✅ Delete Product (Admin Only)
class DeleteProductView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]