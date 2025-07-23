from django.urls import path, include
# from .menu import driver_app_menu
from .edit import driver_app_order_api_edit
from .list import driver_app_order_api_list


urlpatterns = [
    path('edit/', driver_app_order_api_edit, name="driver_app_order_api_edit"),
    path('list/', driver_app_order_api_list, name="driver_app_order_api_list"),
]
