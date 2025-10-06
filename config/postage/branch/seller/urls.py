from django.urls import path, include

from .details import postage_branch_seller_details
from .history import postage_branch_seller_history
from .input import postage_branch_seller_input, postage_branch_seller_input_api
from .postage_return import postage_seller_return, postage_seller_return_api

urlpatterns = [
#     # products
    path('history/<int:logistic_branch_id>', postage_branch_seller_history, name="postage_branch_seller_history"),
    path('input/<int:logistic_branch_id>/<int:postage_id>', postage_branch_seller_input, name="postage_branch_seller_input"),
    path('input/api/<int:logistic_branch_id>/<int:postage_id>', postage_branch_seller_input_api, name="postage_branch_seller_input_api"),
    path('details/<int:logistic_branch_id>/<int:postage_id>', postage_branch_seller_details, name="postage_branch_seller_details"),

    path('return/<int:logistic_branch_id>/<int:seller_id>', postage_seller_return, name="postage_seller_return"),
    path('return/api/<int:logistic_branch_id>/<int:seller_id>', postage_seller_return_api, name="postage_seller_return_api"),
]
