from rest_framework import generics
from .models import Sport, Position
from .serializers import SportSerializer, PositionSerializer
from .permissions import IsSuperAdmin  # Import the custom permission

# ✅ List Sports (Anyone) & Create Sports (Superadmin Only)
class SportListCreateView(generics.ListCreateAPIView):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [IsSuperAdmin]  # Only superadmin can add

    def perform_create(self, serializer):
        serializer.save()  # Assign creator

# ✅ Retrieve, Update, Delete a Specific Sport (Superadmin Only)
class SportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [IsSuperAdmin]

# ✅ List Positions for a Sport (Anyone) & Add Position (Superadmin Only)
class PositionListCreateView(generics.ListCreateAPIView):
    serializer_class = PositionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        sport_id = self.kwargs["sport_id"]
        return Position.objects.filter(sport_id=sport_id)

    def perform_create(self, serializer):
        sport_id = self.kwargs["sport_id"]
        serializer.save(sport_id=sport_id)

# ✅ Retrieve, Update, Delete a Specific Position (Superadmin Only)
class PositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsSuperAdmin]