
from django.contrib import admin
from django.urls import path, include

from .order_confirmed import stream_order_confirmed
from .order_create import stream_order_create
urlpatterns = [
    path('<str:url>/', stream_order_create, name="stream_order_create"),
    path('confirmed/<str:order_id>/', stream_order_confirmed, name="stream_order_confirmed"),
]