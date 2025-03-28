from django.urls import path
from .views import (
    CreateProductView,
    ListProductsView,
    RetrieveProductView,
    UpdateProductView,
    DeleteProductView,
    CheckProductNameView,
)

urlpatterns = [
    path("add/", CreateProductView.as_view(), name="add-product"),  # ✅ Create product
    path("list/", ListProductsView.as_view(), name="list-products"),  # ✅ List all products
    path("<int:pk>/", RetrieveProductView.as_view(), name="retrieve-product"),  # ✅ Get single product
    path("<int:pk>/update/", UpdateProductView.as_view(), name="update-product"),  # ✅ Update product
    path("<int:pk>/delete/", DeleteProductView.as_view(), name="delete-product"),  # ✅ Delete product
    path("check-name/", CheckProductNameView.as_view(), name="check-product-name"),
]