from django.contrib import admin
from django.urls import path, include

from .details import seller_details
from .list import seller_list
from .create import seller_create
from .edit import seller_edit
from .statistic_list import seller_statistic_list

urlpatterns = [
    path('list/', seller_list, name='seller_list'),
    path('statistic-list/', seller_statistic_list, name='seller_statistic_list'),
    path('create/', seller_create, name='seller_create'),
    path('edit/<int:id>', seller_edit, name='seller_edit'),
    path('details/<int:id>', seller_details, name='seller_details'),
    path('product/', include('config.seller.product.urls')),
]