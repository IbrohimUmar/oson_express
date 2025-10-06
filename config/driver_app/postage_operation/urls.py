from django.urls import path, include
from .history import driver_app_postage_operation_history
from .input import driver_app_postage_operation_input, driver_app_postage_operation_input_api
from .details import driver_app_postage_operation_details
from .return_postage import driver_app_postage_operation_return, driver_app_postage_operation_return_api

urlpatterns = [
    path('history/', driver_app_postage_operation_history, name="driver_app_postage_operation_history"),
    path('input/<int:postage_id>', driver_app_postage_operation_input, name="driver_app_postage_operation_input"),
    path('details/<int:postage_id>', driver_app_postage_operation_details, name="driver_app_postage_operation_details"),
    path('input/<int:postage_id>/api', driver_app_postage_operation_input_api, name="driver_app_postage_operation_input_api"),

    path('return/', driver_app_postage_operation_return, name="driver_app_postage_operation_return"),
    path('return/api/', driver_app_postage_operation_return_api, name="driver_app_postage_operation_return_api"),
]