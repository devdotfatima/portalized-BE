# # chat/views.py
# from rest_framework import viewsets, status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from drf_yasg.utils import swagger_auto_schema
# from .models import Chat
# from .serializers import ChatSerializer


# class ChatViewSet(viewsets.ModelViewSet):
#     serializer_class = ChatSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         if getattr(self, 'swagger_fake_view', False):
#             return Chat.objects.none()  # Return an empty queryset during schema generation
#         user = self.request.user
#         # This is the base queryset: all chats the user is in
#         return Chat.objects.filter(participant_1=user) | Chat.objects.filter(participant_2=user)

#     @swagger_auto_schema(operation_description="Get list of unique chats for the logged-in user")
#     def list(self, request, *args, **kwargs):
#         user = request.user
#         all_chats = self.get_queryset()

#         seen_pairs = set()
#         unique_chats = []

#         for chat in all_chats:
#             pair = tuple(sorted([chat.participant_1.id, chat.participant_2.id]))
#             if pair not in seen_pairs:
#                 seen_pairs.add(pair)
#                 unique_chats.append(chat)

#         serializer = self.get_serializer(unique_chats, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @swagger_auto_schema(operation_description="Create a new chat")
#     def create(self, request, *args, **kwargs):
#         return super().create(request, *args, **kwargs)

#     @swagger_auto_schema(operation_description="Retrieve a single chat by ID")
#     def retrieve(self, request, *args, **kwargs):
#         return super().retrieve(request, *args, **kwargs)

#     @swagger_auto_schema(operation_description="Update a chat by ID (full update)")
#     def update(self, request, *args, **kwargs):
#         return super().update(request, *args, **kwargs)

#     @swagger_auto_schema(operation_description="Partially update a chat by ID")
#     def partial_update(self, request, *args, **kwargs):
#         return super().partial_update(request, *args, **kwargs)

#     @swagger_auto_schema(operation_description="Delete a chat by ID")
#     def destroy(self, request, *args, **kwargs):
#         return super().destroy(request, *args, **kwargs)


# views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Chat
from .serializers import ChatSerializer

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Chat.objects.none()
        return Chat.objects.filter(participants=self.request.user)

    @swagger_auto_schema(operation_description="Get list of chats for the logged-in user")
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description="Create a new chat")
    def create(self, request, *args, **kwargs):
        # Optional: Prevent creating a chat with yourself or more than 2 participants
        participants = request.data.get("participants", [])
        if request.user.id not in participants:
            participants.append(request.user.id)
        if len(participants) > 2:
            return Response(
                {"detail": "Only 2 participants allowed in a chat."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)