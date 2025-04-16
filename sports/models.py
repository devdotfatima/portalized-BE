from django.db import models

class Sport(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "gender")  # Ensures uniqueness per gender

    def __str__(self):
        return f"{self.name} ({self.gender})"


class Position(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="positions")  # Link to a specific sport
    name = models.CharField(max_length=255)  # Position name

    class Meta:
        unique_together = ("sport", "name")  # Prevent duplicate positions for the same sport

    def __str__(self):
        return f"{self.name} ({self.sport.name})"