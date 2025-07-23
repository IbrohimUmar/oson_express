from os import path

from django.urls import path, include
# from config.diver_app.payment import create,
from config.driver_app.payment.create import  driver_app_payment_create
from config.driver_app.payment.history import  driver_app_payment_history

urlpatterns = [
    path('history', driver_app_payment_history, name="driver_app_payment_history"),
    path('create', driver_app_payment_create, name="driver_app_payment_create")
]