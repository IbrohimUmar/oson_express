from django.urls import path, include
from .main import driver_warehouse
from .operation.history import driver_warehouse_operation_history, driver_warehouse_operation_history_details_by_order, driver_warehouse_operation_history_details_by_product
from .operation.send_product.create import driver_warehouse_operation_send_product_create_camera, driver_warehouse_operation_send_product_create_scanner
from .operation.send_product.create_api import driver_warehouse_operation_send_product_create_api
from .operation.return_product.by_order_create import driver_warehouse_operation_return_product_by_order_create_scanner
from .operation.return_product.by_order_create_api import driver_warehouse_operation_return_product_by_order_create_api



urlpatterns = [
    # products
    path('main/<int:driver_id>', driver_warehouse, name='driver_warehouse'),
    path('operation/history/<int:driver_id>', driver_warehouse_operation_history, name='driver_warehouse_operation_history'),
    path('operation/history/details/by-order/<int:driver_id>/<int:warehouse_operation_id>', driver_warehouse_operation_history_details_by_order, name='driver_warehouse_operation_history_details_by_order'),
    path('operation/history/details/by-product/<int:driver_id>/<int:warehouse_operation_id>', driver_warehouse_operation_history_details_by_product, name='driver_warehouse_operation_history_details_by_product'),

    path('operation/send-product/create/camera/<int:driver_id>', driver_warehouse_operation_send_product_create_camera, name='driver_warehouse_operation_send_product_create_camera'),
    path('operation/send-product/create/scanner/<int:driver_id>', driver_warehouse_operation_send_product_create_scanner, name='driver_warehouse_operation_send_product_create_scanner'),
    path('operation/send-product/create/api/<int:driver_id>', driver_warehouse_operation_send_product_create_api, name='driver_warehouse_operation_send_product_create_api'),

    path('operation/return-product/create/scanner/<int:driver_id>', driver_warehouse_operation_return_product_by_order_create_scanner,
         name='driver_warehouse_operation_return_product_by_order_create_scanner'),

    path('operation/return-product/create/api/<int:driver_id>', driver_warehouse_operation_return_product_by_order_create_api,
         name='driver_warehouse_operation_return_product_by_order_create_api'),

]