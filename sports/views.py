from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Sport, Position
from rest_framework import permissions
from .serializers import SportSerializer, PositionSerializer
from .permissions import IsSuperAdmin  # Import the custom permission

gender_param = openapi.Parameter(
    'gender',
    openapi.IN_QUERY,
    description="Filter sports by gender (e.g., male, female)",
    type=openapi.TYPE_STRING
)
class SportListCreateView(generics.ListCreateAPIView):
    serializer_class = SportSerializer

    @swagger_auto_schema(
        operation_description="List all sports. Optionally filter by gender using ?gender=male|female|other",
        manual_parameters=[gender_param],
        responses={200: SportSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new sport (Superadmin only)",
        request_body=SportSerializer,
        responses={201: SportSerializer}
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Sport.objects.all()
        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSuperAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save()

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