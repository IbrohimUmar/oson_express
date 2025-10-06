from django.urls import path, include
from .list import marketer_app_payment_list
from .create import marketer_app_payment_create
urlpatterns = [
    path('list/', marketer_app_payment_list, name="marketer_app_payment_list"),
    path('create/', marketer_app_payment_create, name="marketer_app_payment_create"),
]