from django.urls import path, include
from .create import seller_app_operator_payment_create
from .list import seller_app_operator_payment_list


urlpatterns = [
    path('list/<int:operator_id>', seller_app_operator_payment_list,name='seller_app_operator_payment_list'),
    path('create/<int:operator_id>/', seller_app_operator_payment_create, name='seller_app_operator_payment_create'),
]