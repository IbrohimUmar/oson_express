from django.urls import path, include
from .list import marketer_app_product_list
from .details import marketer_app_product_details
urlpatterns = [
    # products
    path('list/', marketer_app_product_list, name="marketer_app_product_list"),
    path('details/<int:product_id>', marketer_app_product_details, name="marketer_app_product_details"),
]