from django.contrib import admin
from django.urls import path, include
from .all import seller_app_orders_list_all
from .canceled import seller_app_orders_list_canceled
from .sold import seller_app_orders_list_sold
from .double import seller_app_orders_list_double
from .delayed_delivery import seller_app_orders_list_delayed_delivery
from .late_wrehouse_exit import seller_app_orders_list_late_warehouse_exit

urlpatterns = [
    path('all/', seller_app_orders_list_all, name="seller_app_orders_list_all"),
    path('canceled/', seller_app_orders_list_canceled, name="seller_app_orders_list_canceled"),
    path('sold/', seller_app_orders_list_sold, name="seller_app_orders_list_sold"),
    path('double/', seller_app_orders_list_double, name="seller_app_orders_list_double"),
    path('delayed-delivery/', seller_app_orders_list_delayed_delivery, name="seller_app_orders_list_delayed_delivery"),
    path('late-warehouse-exit/', seller_app_orders_list_late_warehouse_exit, name="seller_app_orders_list_late_warehouse_exit"),
]