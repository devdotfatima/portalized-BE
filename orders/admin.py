from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress

# Inline model to display Order Items inside Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra blank rows
    readonly_fields = ("product", "quantity", "price_at_purchase")  # Read-only fields

# Custom Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "status", "created_at","payment_id")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "id")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]  # Display order items in the order view

# Custom Shipping Address Admin
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("order", "first_name", "last_name", "city", "state", "country", "phone_number")
    search_fields = ("first_name", "last_name", "order__id")

# Register OrderItem separately (optional)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price_at_purchase")
    search_fields = ("order__id", "product__name")  