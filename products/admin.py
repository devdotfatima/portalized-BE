from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "created_at", "updated_at")  # Fields to display in the admin list
    search_fields = ("name",)  # Search by product name
    list_filter = ("created_at", "updated_at")  # Filters for admin
    ordering = ("-created_at",)  # Order by most recent first
    readonly_fields = ("created_at", "updated_at")  # Make timestamps read-only