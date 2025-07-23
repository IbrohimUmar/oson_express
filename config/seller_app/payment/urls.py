from django.urls import path, include
from .list import seller_app_payment_list
from .create import seller_app_payment_create
urlpatterns = [
    path('list/', seller_app_payment_list, name="seller_app_payment_list"),
    path('create/', seller_app_payment_create, name="seller_app_payment_create"),
]