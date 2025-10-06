from django.urls import path, include
from .list import marketer_app_stream_list
urlpatterns = [
    # products
    path('list/', marketer_app_stream_list, name="marketer_app_stream_list"),
]