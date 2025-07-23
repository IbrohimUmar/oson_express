from django.urls import path, include
from .list import seller_payment_list
from .details import seller_payment_details
urlpatterns = [
    path('list/', seller_payment_list, name="seller_payment_list"),
    path('details/<int:payment_id>', seller_payment_details, name="seller_payment_details"),
]