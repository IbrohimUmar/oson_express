from django.urls import path, include
from .main import driver_send_barcode_main
from .main_api import driver_send_barcode_main_api

urlpatterns = [
    # products
    path('main/', driver_send_barcode_main, name='driver_send_barcode_main'),
    path('main/api', driver_send_barcode_main_api, name='driver_send_barcode_main_api'),

]