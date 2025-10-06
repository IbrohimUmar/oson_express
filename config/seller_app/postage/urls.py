#
from django.urls import path, include
from .history import seller_app_postage_history
from .input import seller_app_postage_input, seller_app_postage_input_api
from .details import seller_app_postage_details
from .postage_return import seller_app_postage_return, seller_app_postage_return_api
urlpatterns = [
    # products
    path('history/', seller_app_postage_history, name="seller_app_postage_history"),
    path('input/', seller_app_postage_input, name="seller_app_postage_input"),
    path('details/<int:postage_id>', seller_app_postage_details, name="seller_app_postage_details"),
    path('input/api/', seller_app_postage_input_api, name="seller_app_postage_input_api"),

    path('return/<int:postage_id>', seller_app_postage_return, name="seller_app_postage_return"),
    path('return/api/<int:postage_id>', seller_app_postage_return_api, name="seller_app_postage_return_api"),
]