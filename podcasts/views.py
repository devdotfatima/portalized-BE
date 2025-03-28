from rest_framework.views import APIView
from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Podcast,PodcastLike,PodcastComment
from .serializers import PodcastSerializer,PodcastCommentSerializer,PodcastLikeSerializer


class UploadPodcastView(APIView):
    """Admin uploads a new Podcast."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        print(request.data)
        serializer = PodcastSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response({"message": "Podcast uploaded successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePodcastView(APIView):
    """Admin can update podcast details (cover image, title, description)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, podcast_id):
        try:
            podcast = Podcast.objects.get(id=podcast_id)
        except Podcast.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Extract fields from request
        title = request.data.get("title", podcast.title)  # Keep existing if not provided
        description = request.data.get("description", podcast.description)
        cover_image = request.data.get("cover_image", podcast.cover_image)  # URL

        # ✅ Update fields
        podcast.title = title
        podcast.description = description
        podcast.cover_image = cover_image
        podcast.save()

        return Response({"message": "Podcast updated successfully", "data": PodcastSerializer(podcast).data}, status=status.HTTP_200_OK)


class ListPodcastsView(generics.ListAPIView):
    """Retrieve a list of all podcasts with filtering, search, and pagination."""
    queryset = Podcast.objects.all().order_by("-created_at")
    serializer_class = PodcastSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # ✅ Filter by uploader, views
    filterset_fields = ["uploaded_by", "views"]

    # ✅ Search by title and description
    search_fields = ["title", "description"]

    # ✅ Sorting options
    ordering_fields = ["title", "views", "created_at"]


class GetPodcastDetailView(generics.RetrieveAPIView):
    """Retrieve a single podcast and increment views."""
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1  # ✅ Increment views
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ToggleLikeDislikeView(APIView):
    """Users can like, dislike, or remove their reaction."""
    permission_classes = [IsAuthenticated]

    def post(self, request, podcast_id):
        try:
            podcast = Podcast.objects.get(id=podcast_id)
        except Podcast.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)

        is_liked = request.data.get("is_liked")  # True for Like, False for Dislike

        if is_liked is None:
            return Response({"error": "is_liked is required (True for Like, False for Dislike)"}, status=status.HTTP_400_BAD_REQUEST)

        like_obj, created = PodcastLike.objects.get_or_create(user=request.user, podcast=podcast)

        if not created:
            # ✅ If user is trying to toggle to the **same reaction** (like → like or dislike → dislike), remove it
            if like_obj.is_liked == is_liked:
                like_obj.delete()
                return Response({"message": "Reaction removed"}, status=status.HTTP_200_OK)
            
            # ✅ Otherwise, change the reaction (like → dislike or dislike → like)
            like_obj.is_liked = is_liked
            like_obj.save()
            return Response({"message": "Reaction updated", "is_liked": like_obj.is_liked}, status=status.HTTP_200_OK)

        # ✅ If new reaction is added (first time like/dislike)
        like_obj.is_liked = is_liked
        like_obj.save()
        return Response({"message": "Reaction added", "is_liked": like_obj.is_liked}, status=status.HTTP_201_CREATED)
    

class AddCommentView(APIView):
    """Users can add a comment on a podcast."""
    permission_classes = [IsAuthenticated]

    def post(self, request, podcast_id):
        try:
            podcast = Podcast.objects.get(id=podcast_id)
        except Podcast.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get("content")
        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

        comment = PodcastComment.objects.create(user=request.user, podcast=podcast, content=content)

        return Response({"message": "Comment added successfully", "comment": comment.content}, status=status.HTTP_201_CREATED)
    

class GetCommentsView(generics.ListAPIView):
    """Retrieve comments for a specific podcast."""
    serializer_class = PodcastCommentSerializer

    def get_queryset(self):
        podcast_id = self.kwargs["podcast_id"]
        return PodcastComment.objects.filter(podcast_id=podcast_id).order_by("-created_at")
    

class DeleteCommentView(APIView):
    """Users can delete their comments, and admins can delete any comment."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        try:
            comment = PodcastComment.objects.get(id=comment_id)
        except PodcastComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user == comment.user or request.user.is_superuser:
            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "You are not allowed to delete this comment"}, status=status.HTTP_403_FORBIDDEN)
    

class DeletePodcastView(APIView):
    """Admin can delete a podcast."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, podcast_id):
        try:
            podcast = Podcast.objects.get(id=podcast_id)
        except Podcast.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)

        podcast.delete()
        return Response({"message": "Podcast deleted successfully"}, status=status.HTTP_200_OK)
        