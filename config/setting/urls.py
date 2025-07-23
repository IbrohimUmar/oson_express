from django.urls import path, include
from .product import setting_product_details_api, setting_product_list, setting_product_create, setting_product_edit


urlpatterns = [
    path('setting/product/list', setting_product_list, name="setting_product_list"),
    path('setting/product/create', setting_product_create, name="setting_product_create"),
    path('setting/product/edit/<int:id>', setting_product_edit, name="setting_product_edit"),
    path('setting/product/details/api/', setting_product_details_api, name="setting_product_details_api"),

]