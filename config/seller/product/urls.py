from django.contrib import admin
from django.urls import path, include
from .list import seller_product_list
from .details import seller_product_details
# from .list import seller_list
# from .create import seller_create
# from .edit import seller_edit
urlpatterns = [
    path('<int:seller_id>/list/', seller_product_list, name='seller_product_list'),
    path('<int:seller_id>/details/<int:product_id>', seller_product_details, name='seller_product_details'),
    # path('create/', seller_create, name='seller_create'),
]