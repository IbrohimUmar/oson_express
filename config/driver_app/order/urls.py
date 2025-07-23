from django.urls import path, include
# from .menu import driver_app_menu
from .main import driver_app_order_main


urlpatterns = [
    path('main', driver_app_order_main, name="driver_app_order_main"),
    path('api/', include('config.driver_app.order.api.urls')),
]
