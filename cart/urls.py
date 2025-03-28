from django.urls import path
from .views import GetCartView, AddToCartView, UpdateCartItemView, ClearCartView,DeleteCartItemView

urlpatterns = [
    path("", GetCartView.as_view(), name="get-cart"),
    path("add/", AddToCartView.as_view(), name="add-to-cart"),
    path("update/<int:item_id>/", UpdateCartItemView.as_view(), name="update-cart"),
    path("remove/<int:item_id>/", DeleteCartItemView.as_view(), name="update-cart"),
    path("delete", ClearCartView.as_view(), name="clear-cart"),
]