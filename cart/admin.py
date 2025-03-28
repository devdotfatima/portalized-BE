from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):  # ✅ Display CartItems inside Cart
    model = CartItem
    extra = 0  # ✅ Prevent empty extra rows
    fields = ("product", "quantity", "price_at_purchase")
    readonly_fields = ("price_at_purchase",)  # ✅ Prevent manual editing of price

class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")  # ✅ Show user and cart creation date
    inlines = [CartItemInline]  # ✅ Display CartItems inside Cart

admin.site.register(Cart, CartAdmin)  # ✅ Register Cart with custom display