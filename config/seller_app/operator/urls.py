from django.urls import path, include
from .details import seller_app_operator_details, seller_app_operator_details_order
from .create import seller_app_operator_create
from .edit import seller_app_operator_edit
from .list import seller_app_operator_list
from .statistic_list import seller_app_operator_statistic_list
from .date_by_statistic_list import seller_app_operator_date_by_statistic


urlpatterns = [

    path('payment/', include('config.seller_app.operator.payment.urls')),

    path('statistic-list/', seller_app_operator_statistic_list, name='seller_app_operator_statistic_list'),
    path('date-by-statistic-list/', seller_app_operator_date_by_statistic, name='seller_app_operator_date_by_statistic'),

    path('list/', seller_app_operator_list, name='seller_app_operator_list'),
    path('create/', seller_app_operator_create, name='seller_app_operator_create'),
    path('edit/<int:id>/', seller_app_operator_edit, name='seller_app_operator_edit'),
    path('details/<int:id>/', seller_app_operator_details, name='seller_app_operator_details'),
    path('details/<int:id>/<int:year>/<int:month>/<int:day>', seller_app_operator_details_order, name='seller_app_operator_details_order'),
]