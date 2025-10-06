from django.contrib import admin
from django.urls import path, include
from .edit import seller_app_order_edit
from .details import seller_app_order_details
from .print import seller_app_order_print


urlpatterns = [
    path('list/', include('config.seller_app.orders.list.urls')),
    path('edit/<int:id>', seller_app_order_edit, name="seller_app_order_edit"),
    path('details/<int:id>', seller_app_order_details, name="seller_app_order_details"),
    path('print/<int:id>', seller_app_order_print, name="seller_app_order_print"),
]