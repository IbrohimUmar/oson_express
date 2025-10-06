from django.urls import path
from config.seller_app.warehouse.purchase import main

urlpatterns = [
    path('main', main.seller_app_warehouse_purchase_main, name="seller_app_warehouse_purchase_main"),
]