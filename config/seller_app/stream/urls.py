from django.urls import path, include
from .list import seller_app_stream_list
urlpatterns = [
    # products
    path('list/', seller_app_stream_list, name="seller_app_stream_list"),
]