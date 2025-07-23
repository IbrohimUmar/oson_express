from django.urls import path, include
from .list import seller_list
from .create import seller_create
from .edit import seller_edit
urlpatterns = [

    path('payment/', include("config.seller.payment.urls")),
    path('list/', seller_list, name="seller_list"),
    path('create/', seller_create, name="seller_create"),
    path('edit/<int:id>', seller_edit, name="seller_edit"),
    # path('orders/', include('config.driver_app.orders.urls')),

]