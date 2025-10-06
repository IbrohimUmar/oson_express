
from django.urls import path, include
from .history import seller_app_warehouse_order_warehouse_action_history


urlpatterns = [
    path('history/<int:warehouse_id>', seller_app_warehouse_order_warehouse_action_history, name="seller_app_warehouse_order_warehouse_action_history"),
]