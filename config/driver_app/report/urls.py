from django.urls import path

from .main import driver_app_report_main
from .balance_history import driver_app_report_balance_history
urlpatterns = [
    path('main/', driver_app_report_main, name="driver_app_report_main"),
    path('balance_history/', driver_app_report_balance_history, name="driver_app_report_balance_history"),
]