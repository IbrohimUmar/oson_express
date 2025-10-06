from django.urls import path, include
from .order import marketer_app_statistic_order
from .stream import marketer_app_statistic_stream

urlpatterns = [
    path('order/', marketer_app_statistic_order, name="marketer_app_statistic_order"),
    path('stream/', marketer_app_statistic_stream, name="marketer_app_statistic_stream"),
]