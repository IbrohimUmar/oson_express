#
from django.urls import path, include
# from .product_attachment import attachment_create, attachment_details, attachment_history, attachment_print
#
# from config.warehouse import list as warehouse_list
# from config.warehouse.warehouse import residue as warehouse_residue
# from config.warehouse.operation import input as warehouse_operation_input, output as warehouse_operation_output, transit as warehouse_operation_transit, history as warehouse_operation_history
# from config.warehouse.operation.edit import warehouse_operation_edit
# from config.warehouse.product_attachment.scanned_for_packaging import warehouse_product_attachment_scanned_for_packaging, warehouse_product_attachment_scanned_for_packaging_api
#
from .main import postage_main

urlpatterns = [
#     # products
    path('main/', postage_main, name="postage_main"),
    path('branch/', include('config.postage.branch.urls')),
    # path('seller/', include('config.postage.seller.urls')),
#     path('product_attachment/scanned_for_packaging/api', warehouse_product_attachment_scanned_for_packaging_api, name="warehouse_product_attachment_scanned_for_packaging_api"),
#
#     path('product_attachment/print', attachment_print.warehouse_product_attachment_print, name="warehouse_product_attachment_print"),
#     path('product_attachment/print/api', attachment_print.warehouse_product_attachment_print_api, name="warehouse_product_attachment_print_api"),
#     path('product_attachment/print/packaging-order', attachment_print.warehouse_product_attachment_packaging_order_print, name="warehouse_product_attachment_packaging_order_print"),
#
#
#     path('product_attachment/history', attachment_history.warehouse_product_attachment_history, name="warehouse_product_attachment_history"),
#     path('product_attachment/details/<int:id>', attachment_details.warehouse_product_attachment_details, name="warehouse_product_attachment_details"),
#     path('product_attachment/create', attachment_create.warehouse_product_attachment_create, name="warehouse_product_attachment_create"),
#
#     path('purchase/', include('config.warehouse.purchase.urls')),
#     path('order-warehouse-action/', include('config.warehouse.order_warehouse_action.urls')),
#
#     path('list', warehouse_list.warehouse_list, name="warehouse_list"),
#     path('<int:warehouse_id>/operation/input-product',
#          warehouse_operation_input.warehouse_operation_input_product, name="warehouse_operation_input_product"),
#     path('<int:warehouse_id>/operation/output-product',
#          warehouse_operation_output.warehouse_operation_output_product, name="warehouse_operation_output_product"),
#     path('<int:warehouse_id>/operation/transit-product',
#          warehouse_operation_transit.warehouse_operation_transit_product, name="warehouse_operation_transit_product"),
#
#
#     path('<int:warehouse_id>/operation/edit/<int:warehouse_operation_id>', warehouse_operation_edit,
#          name="warehouse_operation_edit"),
#
#     path('<int:warehouse_operation_id>/operation/product/list', warehouse_operation_history.warehouse_operation_product_list,
#          name="warehouse_operation_product_list"),
#     path('<int:warehouse_id>/operation/history', warehouse_operation_history.warehouse_operation_history,
#          name="warehouse_operation_history"),
#     path('<int:warehouse_id>/operation/history/driver', warehouse_operation_history.warehouse_operation_history_driver,
#          name="warehouse_operation_history_driver"),
#
#     path('<int:warehouse_id>/residue', warehouse_residue.warehouse_residue, name="warehouse_residue"),
#
]