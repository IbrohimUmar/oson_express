from django.urls import path, include

from .history import postage_branch_driver_history
from .send import postage_branch_driver_send, postage_branch_driver_send_api
from .details import postage_branch_driver_details
from .postage_return import postage_branch_driver_return, postage_branch_driver_return_api


urlpatterns = [
#     # products
    path('history/<int:logistic_branch_id>', postage_branch_driver_history, name="postage_branch_driver_history"),
    path('details/<int:logistic_branch_id>/<int:postage_id>', postage_branch_driver_details, name="postage_branch_driver_details"),
    path('send/<int:logistic_branch_id>/<int:driver_id>', postage_branch_driver_send, name="postage_branch_driver_send"),
    path('send/api/<int:logistic_branch_id>/<int:driver_id>', postage_branch_driver_send_api, name="postage_branch_driver_send_api"),

    path('return/<int:logistic_branch_id>/<int:postage_id>', postage_branch_driver_return, name="postage_branch_driver_return"),
    path('return/api/<int:logistic_branch_id>/<int:postage_id>', postage_branch_driver_return_api, name="postage_branch_driver_return_api"),

    # path('input/<int:logistic_branch_id>/<int:postage_id>', postage_branch_seller_input, name="postage_branch_seller_input"),
    # path('input/api/<int:logistic_branch_id>/<int:postage_id>', postage_branch_seller_input_api, name="postage_branch_seller_input_api"),
    # path('details/<int:logistic_branch_id>/<int:postage_id>', postage_branch_seller_details, name="postage_branch_seller_details"),
]
