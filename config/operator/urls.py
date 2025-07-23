from django.urls import path, include
from .details import operator_details, operator_details_order
from .create import operator_create
from .edit import operator_edit
from .list import operator_list
from .statistic_list import operator_statistic_list
from .date_by_statistic_list import operator_date_by_statistic


urlpatterns = [

    path('payment/', include('config.operator.payment.urls')),

    path('statistic-list/', operator_statistic_list, name='operator_statistic_list'),
    path('date-by-statistic-list/', operator_date_by_statistic, name='operator_date_by_statistic'),

    path('list/', operator_list, name='operator_list'),
    path('create/', operator_create, name='operator_create'),
    path('edit/<int:id>/', operator_edit, name='operator_edit'),
    path('details/<int:id>/', operator_details, name='operator_details'),
    path('details/<int:id>/<int:year>/<int:month>/<int:day>', operator_details_order, name='operator_details_order'),
]