
from django.contrib import admin
from django.urls import path, include
from .order_create import stream_order_create
urlpatterns = [
    path('<str:url>/', stream_order_create, name="stream_order_create"),
]