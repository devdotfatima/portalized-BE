from django.urls import path
from .views import (
    PlaceOrderView, GetUserOrdersView, GetOrderDetailView, 
    AdminManageOrderView, CreatePaymentIntentView,GetAllOrdersView,StripeWebhookView
)

urlpatterns = [
    path("place-order/", PlaceOrderView.as_view(), name="place-order"),
    path("", GetUserOrdersView.as_view(), name="my-orders"),
    path("<int:order_id>/", GetOrderDetailView.as_view(), name="order-detail"),
    path("manage/admin/<int:order_id>/", AdminManageOrderView.as_view(), name="admin-manage-order"),
    path("payment-intent/", CreatePaymentIntentView.as_view(), name="create-payment-intent"),
    path("admin", GetAllOrdersView.as_view(), name="admin-get-orders"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),

]