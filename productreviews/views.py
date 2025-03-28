from rest_framework import generics, status, filters
from rest_framework.views import APIView
from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from drf_yasg.utils import swagger_auto_schema
from .models import Review
from orders.models import OrderItem
from .serializers import ReviewSerializer,CreateReviewSerializer
from django_filters.rest_framework import DjangoFilterBackend




# class AddReviewView(generics.CreateAPIView):
#     """Allows users to add a review for a product they purchased."""
#     serializer_class = CreateReviewSerializer
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_summary="Add a review",
#         operation_description="Users can review products they have purchased."
#     )
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)

#     def perform_create(self, serializer):
#         """Assign the authenticated user to the review before saving."""
#         serializer.save(user=self.request.user)


# class UpdateReviewView(generics.UpdateAPIView):
#     """Allows users to edit their own review."""
#     serializer_class = ReviewSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         if isinstance(self.request.user, AnonymousUser):
#           return Review.objects.none() 
#         return Review.objects.filter(user=self.request.user)

#     @swagger_auto_schema(operation_summary="Edit a review", operation_description="Users can edit their own reviews.")
#     def put(self, request, *args, **kwargs):
#         return super().put(request, *args, **kwargs)


class UpsertReviewView(generics.RetrieveUpdateAPIView):
    """Allows users to add or update their review for a product they purchased."""
    serializer_class = CreateReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve the existing review for the user and product or return None."""
        product_id = self.kwargs["product_id"]
        user = self.request.user
        return Review.objects.filter(user=user, product_id=product_id).first()

    @swagger_auto_schema(
        operation_summary="Add or update a review",
        operation_description="Users can review products they have purchased. If a review exists, it updates it."
    )
    def put(self, request, *args, **kwargs):
        review = self.get_object()

        if review:
            return super().put(request, *args, **kwargs)

        # If review doesn't exist, create a new one
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ensure the user purchased the product
        product_id = kwargs["product_id"]
        order_item = OrderItem.objects.filter(order__user=request.user, product_id=product_id).first()

        if not order_item:
            return Response({"error": "You can only review products you have purchased."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user, product_id=product_id, order=order_item.order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class DeleteReviewView(generics.DestroyAPIView):
    """Allows users to delete their own reviews, admins can delete any review."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
          return Review.objects.none() 
        user = self.request.user
        if user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=user)

    @swagger_auto_schema(operation_summary="Delete a review", operation_description="Users can delete their own reviews. Admins can delete any review.")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ListProductReviewsView(generics.ListAPIView):
    """Retrieve all reviews for a product."""
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["created_at", "rating"]

    def get_queryset(self):
        # if isinstance(self.request.user, AnonymousUser):
        #   return Review.objects.none() 
        return Review.objects.filter(product_id=self.kwargs["product_id"])

    @swagger_auto_schema(operation_summary="Get reviews for a product", operation_description="Fetches all reviews for a product.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetUserReviewsView(generics.ListAPIView):
    """Retrieve all reviews written by a user."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
           return Review.objects.none() 
        return Review.objects.filter(user=self.request.user)

    @swagger_auto_schema(operation_summary="Get user's reviews", operation_description="Fetches all reviews written by the authenticated user.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetProductReviewStatsView(APIView):
    """Retrieve average rating and review count for a product."""
    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        avg_rating = reviews.aggregate(models.Avg("rating"))["rating__avg"] or 0
        total_reviews = reviews.count()

        return Response({"average_rating": avg_rating, "total_reviews": total_reviews}, status=status.HTTP_200_OK)
    
