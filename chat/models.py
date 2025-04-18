from django.db import models
from authentication.models import User

class Chat(models.Model):
    chat_id = models.IntegerField(unique=True)
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participant_emails = ', '.join([user.email for user in self.participants.all()])
        return f"Chat ({self.chathead_id}) between {participant_emails}"