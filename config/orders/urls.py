from django.contrib import admin
from django.urls import path, include
from .edit import order_edit
from .details import order_details
from .print import order_print


urlpatterns = [
    path('list/', include('config.orders.list.urls')),
    path('edit/<int:id>', order_edit, name="order_edit"),
    path('details/<int:id>', order_details, name="order_details"),
    path('print/<int:id>', order_print, name="order_print"),
]