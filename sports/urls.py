from django.urls import path
from .views import SportListCreateView, SportDetailView, PositionListCreateView, PositionDetailView

urlpatterns = [
    path("/", SportListCreateView.as_view(), name="sport-list-create"),
    path("/<int:pk>/", SportDetailView.as_view(), name="sport-detail"),
    path("/<int:sport_id>/positions/", PositionListCreateView.as_view(), name="position-list-create"),
    path("/positions/<int:pk>/", PositionDetailView.as_view(), name="position-detail"),
]