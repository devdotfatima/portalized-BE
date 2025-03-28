from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.URLField(), required=False)  
    average_rating = serializers.SerializerMethodField()  # ✅ Read-only field
    total_reviews = serializers.SerializerMethodField() 

    class Meta:
        model = Product
        fields = "__all__"  # Includes all fields + computed fields

 
    def get_average_rating(self, obj):
        rating = obj.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        return round(rating, 1) if rating else 0  # Return 0 if no ratings

 
    def get_total_reviews(self, obj):
        return obj.reviews.aggregate(count=Count("id"))["count"]