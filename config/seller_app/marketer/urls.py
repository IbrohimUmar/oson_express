from django.urls import path, include
from .list import seller_app_marketer_list
from .create import seller_app_marketer_create
from .edit import seller_app_marketer_edit
urlpatterns = [
    path('payment/', include("config.seller_app.marketer.payment.urls")),
    path('list/', seller_app_marketer_list, name="seller_app_marketer_list"),
    path('create/', seller_app_marketer_create, name="seller_app_marketer_create"),
    path('edit/<int:id>', seller_app_marketer_edit, name="seller_app_marketer_edit"),
]