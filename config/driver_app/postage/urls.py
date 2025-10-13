from django.urls import path, include
from .input_history import driver_app_postage_input_history
from .order_list import driver_app_postage_order_list
urlpatterns = [
    path('input-history', driver_app_postage_input_history, name="driver_app_postage_input_history"),
    path('<int:id>/order-list', driver_app_postage_order_list, name="driver_app_postage_order_list"),
]