from django.urls import path, include
from .input_history import driver_app_postage_input_history

urlpatterns = [
    path('input-history', driver_app_postage_input_history, name="driver_app_postage_input_history"),
]