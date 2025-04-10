from django.db import models
from authentication.models import User

class Post(models.Model):
    POST_TYPES = (
        ('text', 'Text'),
        ('reel', 'Reel'),
        ('image', 'Image'),
    )

    PRIVACY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True, null=True)
    media_urls = models.JSONField(default=list, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    location = models.CharField(max_length=255, null=True, blank=True) 
    music = models.CharField(max_length=255, null=True, blank=True)  
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')

    def __str__(self):
        return f"{self.user.email} - {self.caption[:20]}"
    
    @property
    def is_liked_by_user(self, user):
        return self.likes.filter(user=user).exists()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)