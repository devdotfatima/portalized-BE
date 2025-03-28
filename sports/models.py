from django.db import models

class Sport(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Unique sport name
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Position(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="positions")  # Link to a specific sport
    name = models.CharField(max_length=255)  # Position name

    class Meta:
        unique_together = ("sport", "name")  # Prevent duplicate positions for the same sport

    def __str__(self):
        return f"{self.name} ({self.sport.name})"