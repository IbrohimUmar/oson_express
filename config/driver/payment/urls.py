from django.urls import path, include
from .create import driver_payment_create
from .list import driver_payment_list

urlpatterns = [
    path('list/<int:id>', driver_payment_list, name='driver_payment_list'),
    path('create/<int:id>', driver_payment_create, name='driver_payment_create'),
]