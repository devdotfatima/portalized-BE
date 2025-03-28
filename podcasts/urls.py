from django.urls import path
from .views import (
    UploadPodcastView, ListPodcastsView, GetPodcastDetailView,
    ToggleLikeDislikeView, AddCommentView, GetCommentsView, DeleteCommentView, UpdatePodcastView, DeletePodcastView
)

urlpatterns = [
    path("/upload/", UploadPodcastView.as_view(), name="upload_video"),  # ✅ Upload Podcast
    path("/", ListPodcastsView.as_view(), name="list_videos"),  # ✅ List Podcasts
    path("/<int:pk>/", GetPodcastDetailView.as_view(), name="get_video"), 
    path("/<int:podcast_id>/update/", UpdatePodcastView.as_view(), name="update podcast"), 
    path("/<int:podcast_id>/delete/", DeletePodcastView.as_view(), name="update podcast"), 
    path("/<int:podcast_id>/like/", ToggleLikeDislikeView.as_view(), name="toggle_like"),  # ✅ Like/Dislike Podcast
    path("/<int:podcast_id>/comments/", GetCommentsView.as_view(), name="get_comments"),  # ✅ Get Comments
    path("/<int:podcast_id>/comment/", AddCommentView.as_view(), name="add_comment"),  # ✅ Add Comment
    path("/comments/<int:comment_id>/delete/", DeleteCommentView.as_view(), name="delete_comment"),  # ✅ Delete Comment
]