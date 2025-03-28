from django.db import models
from authentication.models import User
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")  # ✅ Each user has one cart
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)  # ✅ Ensures quantity can't be negative
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ Store price at the time of adding to cart

    class Meta:
        unique_together = ("cart", "product")  # ✅ Prevent duplicate cart items

    def save(self, *args, **kwargs):
        """Set price_at_purchase when adding the item to cart."""
        if not self.price_at_purchase:
            self.price_at_purchase = self.product.price  # ✅ Capture product price when adding
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} at ${self.price_at_purchase} in {self.cart.user.email}'s cart"