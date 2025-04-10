from django.db import models
from authentication.models import User


class SessionRequest(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_session_requests')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_session_requests')
    session_date = models.DateField()
    session_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.athlete.email} → {self.coach.email} on {self.session_date} at {self.session_time}"