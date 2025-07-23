from django.urls import path, include
from .main_report import driver_main_report


urlpatterns = [
    # products
    path('main/<int:driver_id>', driver_main_report, name='driver_main_report'),

]