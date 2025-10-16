from django.urls import path, include
# from .create import seller_app_operator_payment_create
from .list import seller_app_operator_order_list


urlpatterns = [
    path('list/', seller_app_operator_order_list, name='seller_app_operator_order_list'),
    # path('create/<int:operator_id>/', seller_app_operator_payment_create, name='seller_app_operator_payment_create'),
]