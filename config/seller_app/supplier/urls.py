from django.urls import path, include
from .list import seller_app_supplier_list
from .create import seller_app_supplier_create
from .edit import seller_app_supplier_edit

urlpatterns = [
    path('list/', seller_app_supplier_list, name='seller_app_supplier_list'),
    path('create/', seller_app_supplier_create, name='seller_app_supplier_create'),
    path('edit/<int:id>/', seller_app_supplier_edit, name='seller_app_supplier_edit'),
]