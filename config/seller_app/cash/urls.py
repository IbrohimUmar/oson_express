from django.urls import path, include
from .main import seller_app_cash_main, seller_app_cash_out_data_json, seller_app_cash_filter_json_data, \
    seller_app_cash_report_json_data, seller_app_cash_json_data, seller_app_cash_out_edit_data_json

urlpatterns = [
    path('cash', seller_app_cash_main, name='seller_app_cash_main'),

    path('cash/json-data', seller_app_cash_json_data, name='seller_app_cash_json_data'),
    path('cash/filter/json-data', seller_app_cash_filter_json_data, name='seller_app_cash_filter_json_data'),
    path('cash/report/json-data', seller_app_cash_report_json_data, name='seller_app_cash_report_json_data'),

    path('cash/out/json-data', seller_app_cash_out_data_json, name='seller_app_cash_out_data_json'),
    path('cash/out/edit/json-data', seller_app_cash_out_edit_data_json, name='seller_app_cash_out_edit_data_json'),

]