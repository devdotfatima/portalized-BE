from django.db import models
from authentication.models import User

class Chat(models.Model):
    chathead_id = models.UUIDField(unique=True)  # No default, must be provided
    participant_1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chats_as_participant_1'
    )
    participant_2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chats_as_participant_2'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participant_1', 'participant_2')

    def __str__(self):
        return f"Chat between {self.participant_1.email} & {self.participant_2.email}"