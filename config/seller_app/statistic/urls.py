from django.urls import path, include
from .order import seller_app_statistic_order
from .stream import seller_app_statistic_stream

urlpatterns = [
    path('order/', seller_app_statistic_order, name="seller_app_statistic_order"),
    path('stream/', seller_app_statistic_stream, name="seller_app_statistic_stream"),
]