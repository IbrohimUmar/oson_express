from django.urls import path, include
from config.warehouse.purchase import main

urlpatterns = [
    path('main', main.warehouse_purchase_main, name="warehouse_purchase_main"),
]