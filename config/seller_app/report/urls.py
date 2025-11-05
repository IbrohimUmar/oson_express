from django.urls import path, include
from .main import seller_app_report_main

urlpatterns = [
    path('main/', seller_app_report_main, name='seller_app_report_main'),
    # path('create/', seller_app_supplier_create, name='seller_app_supplier_create'),
]