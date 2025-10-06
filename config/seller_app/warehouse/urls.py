
from django.urls import path, include
from .product_attachment import attachment_create, attachment_details, attachment_history, attachment_print

from . import list as warehouse_list
from .warehouse import residue as warehouse_residue
from .operation import output as warehouse_operation_output, transit as warehouse_operation_transit, \
    input as warehouse_operation_input, history as warehouse_operation_history
from config.seller_app.warehouse.operation.edit import seller_app_warehouse_operation_edit
from config.seller_app.warehouse.product_attachment.scanned_for_packaging import seller_app_warehouse_product_attachment_scanned_for_packaging, seller_app_warehouse_product_attachment_scanned_for_packaging_api

urlpatterns = [
    # products
    path('product_attachment/scanned_for_packaging', seller_app_warehouse_product_attachment_scanned_for_packaging, name="seller_app_warehouse_product_attachment_scanned_for_packaging"),
    path('product_attachment/scanned_for_packaging/api', seller_app_warehouse_product_attachment_scanned_for_packaging_api, name="seller_app_warehouse_product_attachment_scanned_for_packaging_api"),

    path('product_attachment/print', attachment_print.seller_app_warehouse_product_attachment_print, name="seller_app_warehouse_product_attachment_print"),
    path('product_attachment/print/api', attachment_print.seller_app_warehouse_product_attachment_print_api, name="seller_app_warehouse_product_attachment_print_api"),
    path('product_attachment/print/packaging-order', attachment_print.seller_app_warehouse_product_attachment_packaging_order_print, name="seller_app_warehouse_product_attachment_packaging_order_print"),


    path('product_attachment/history', attachment_history.seller_app_warehouse_product_attachment_history, name="seller_app_warehouse_product_attachment_history"),
    path('product_attachment/details/<int:id>', attachment_details.seller_app_warehouse_product_attachment_details, name="seller_app_warehouse_product_attachment_details"),
    path('product_attachment/create', attachment_create.seller_app_warehouse_product_attachment_create, name="seller_app_warehouse_product_attachment_create"),

    path('purchase/', include('config.seller_app.warehouse.purchase.urls')),
    path('order-warehouse-action/', include('config.seller_app.warehouse.order_warehouse_action.urls')),

    path('list', warehouse_list.seller_app_warehouse_list, name="seller_app_warehouse_list"),
    path('<int:warehouse_id>/operation/input-product',
         warehouse_operation_input.seller_app_warehouse_operation_input_product, name="seller_app_warehouse_operation_input_product"),
    path('<int:warehouse_id>/operation/output-product',
         warehouse_operation_output.seller_app_warehouse_operation_output_product, name="seller_app_warehouse_operation_output_product"),
    path('<int:warehouse_id>/operation/transit-product',
         warehouse_operation_transit.seller_app_warehouse_operation_transit_product, name="seller_app_warehouse_operation_transit_product"),


    path('<int:warehouse_id>/operation/edit/<int:warehouse_operation_id>', seller_app_warehouse_operation_edit,
         name="seller_app_warehouse_operation_edit"),

    path('<int:warehouse_operation_id>/operation/product/list', warehouse_operation_history.seller_app_warehouse_operation_product_list,
         name="seller_app_warehouse_operation_product_list"),
    path('<int:warehouse_id>/operation/history', warehouse_operation_history.seller_app_warehouse_operation_history,
         name="seller_app_warehouse_operation_history"),
    path('<int:warehouse_id>/operation/history/driver', warehouse_operation_history.seller_app_warehouse_operation_history_driver,
         name="seller_app_warehouse_operation_history_driver"),

    path('<int:warehouse_id>/residue', warehouse_residue.seller_app_warehouse_residue, name="seller_app_warehouse_residue"),

]