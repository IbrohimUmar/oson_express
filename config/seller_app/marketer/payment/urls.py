from django.urls import path, include
from .list import seller_app_marketer_payment_list
from .details import seller_app_marketer_payment_details
urlpatterns = [
    path('list/', seller_app_marketer_payment_list, name="seller_app_marketer_payment_list"),
    path('details/<int:payment_id>', seller_app_marketer_payment_details, name="seller_app_marketer_payment_details"),
]