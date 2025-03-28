from django.db import models
from authentication.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)


    # Payment
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # 'stripe', 'paypal'
    payment_status = models.CharField(max_length=50, blank=True, null=True)  # 'succeeded', 'failed'
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    receipt_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ Store price at checkout

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping_address")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"Shipping for Order {self.order.id} - {self.full_name}"