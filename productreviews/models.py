from django.db import models
from authentication.models import User
from products.models import Product
from orders.models import Order

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reviews")  
    rating = models.PositiveIntegerField()  # ⭐ Rating (1-5)
    review_text = models.TextField(blank=True, null=True)  # Optional review text
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")  # Prevent duplicate reviews

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}⭐)"