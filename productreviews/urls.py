from django.urls import path
from .views import (
      DeleteReviewView,
    ListProductReviewsView, GetUserReviewsView, GetProductReviewStatsView,UpsertReviewView
)

urlpatterns = [
    path("add/<int:product_id>/", UpsertReviewView.as_view(), name="add_review"),
    # path("edit/<int:pk>/", UpdateReviewView.as_view(), name="edit_review"),
    path("delete/<int:pk>/", DeleteReviewView.as_view(), name="delete_review"),
    path("product/<int:product_id>/", ListProductReviewsView.as_view(), name="product_"),
    path("user/", GetUserReviewsView.as_view(), name="user_"),
    path("product/<int:product_id>/stats/", GetProductReviewStatsView.as_view(), name="product_review_stats"),
]