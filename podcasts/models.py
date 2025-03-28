from django.db import models
from authentication.models import User

class Podcast(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    firebase_url = models.URLField()  
    cover_image = models.URLField(blank=True, null=True) 
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class PodcastLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name="likes")
    is_liked = models.BooleanField(default=True)  # True for Like, False for Dislike

    class Meta:
        unique_together = ("user", "podcast")


class PodcastComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} on {self.podcast.title}"