from django.urls import path, include
from .setting_product_details_api import setting_product_details_api
urlpatterns = [
    path('setting/product/details/api/', setting_product_details_api, name="setting_product_details_api"),
]