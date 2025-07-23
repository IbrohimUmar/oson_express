from django.urls import path, include
from .history import driver_order_history

urlpatterns = [
    path('history/<int:driver_id>', driver_order_history, name='driver_order_history'),
]