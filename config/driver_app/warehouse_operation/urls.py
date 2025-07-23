from django.urls import path, include
from .list import driver_app_warehouse_operation_list
from .product_list import driver_app_warehouse_operation_product_list
from .order_list import driver_app_warehouse_operation_order_list
urlpatterns = [
    path('list', driver_app_warehouse_operation_list, name="driver_app_warehouse_operation_list"),
    path('<int:warehouse_operation_id>/product-list', driver_app_warehouse_operation_product_list, name="driver_app_warehouse_operation_product_list"),
    path('<int:warehouse_operation_id>/order-list', driver_app_warehouse_operation_order_list, name="driver_app_warehouse_operation_order_list"),
]