#
from django.urls import path, include
from .list import order_list
from .sold_list import order_sold_list
from ._print import order_print
urlpatterns = [
#     # order
    path('list/', order_list, name="order_list"),
    path('sold-list/', order_sold_list, name="order_sold_list"),
    path('print/<int:id>', order_print, name="order_print"),
]