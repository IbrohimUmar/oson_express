from django.urls import path, include
from .list import seller_app_product_list
from .details import seller_app_product_details
urlpatterns = [
    # products
    path('list/', seller_app_product_list, name="seller_app_product_list"),
    path('details/<int:product_id>', seller_app_product_details, name="seller_app_product_details"),
]