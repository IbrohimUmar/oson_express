from django.urls import path, include
from .create import operator_payment_create
from .list import operator_payment_list


urlpatterns = [
    path('list/<int:operator_id>', operator_payment_list,name='operator_payment_list'),
    path('create/<int:operator_id>/', operator_payment_create, name='operator_payment_create'),
]