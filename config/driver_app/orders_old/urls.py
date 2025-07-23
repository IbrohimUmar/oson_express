from django.urls import path, include
# from .menu import driver_app_menu
from .scanner_cancel import driver_app_order_scanner_cancel, driver_app_order_scanner_cancel_api
from .main import driver_app_order_list
from .api import driver_app_order_list_api

urlpatterns = [
    path('scanner-cancel', driver_app_order_scanner_cancel, name="driver_app_order_scanner_cancel"),
    path('scanner-cancel-api', driver_app_order_scanner_cancel_api, name="driver_app_order_scanner_cancel_api"),
    path('list', driver_app_order_list, name="driver_app_order_list"),
    path('api/list', driver_app_order_list_api, name="driver_app_order_list_api"),
    # path('residue', driver_app_warehouse_residue, name="driver_app_warehouse_residue"),

    # path('menu/', driver_app_menu, name="driver_app_menu"),
]