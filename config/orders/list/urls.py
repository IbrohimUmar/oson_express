from django.contrib import admin
from django.urls import path, include
from .all import orders_list_all
from .canceled import orders_list_canceled
from .sold import orders_list_sold
from .double import orders_list_double
from .delayed_delivery import orders_list_delayed_delivery
from .late_wrehouse_exit import orders_list_late_warehouse_exit

urlpatterns = [
    path('all/', orders_list_all, name="orders_list_all"),
    path('canceled/', orders_list_canceled, name="orders_list_canceled"),
    path('sold/', orders_list_sold, name="orders_list_sold"),
    path('double/', orders_list_double, name="orders_list_double"),
    path('delayed-delivery/', orders_list_delayed_delivery, name="orders_list_delayed_delivery"),
    path('late-warehouse-exit/', orders_list_late_warehouse_exit, name="orders_list_late_warehouse_exit"),
]