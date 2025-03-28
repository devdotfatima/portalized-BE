from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "order", "rating", "created_at")  # Fields shown in the admin list view
    search_fields = ("user__email", "product__name", "order__id")  # Enable searching by user email, product name, and order ID
    list_filter = ("rating", "created_at")  # Filters for easier navigation
    ordering = ("-created_at",)  # Order by newest reviews first
    readonly_fields = ("created_at",)  # Prevent modification of creation date