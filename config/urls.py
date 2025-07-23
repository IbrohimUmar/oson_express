from django.contrib import admin
from django.urls import path, include
from .views import home, login
from django.conf.urls.static import static
from . import settings
# from config.operator import operator
from config.settings.base import MEDIA_ROOT, MEDIA_URL, SITE_NAME
from config.report import report, big_balance as report_big_balance
from .excel import excel
from config.cash import main as cash_main
from config.connection.order_on_other_sites import CreateOrderFromOtherSite, check_order, check_changed_order
from config.shopkeeper.manage import crud as shopkeeper_crud
from config.driver import daily_report as driver_daily_report
from config.orders import print_unshipped_orders
from config.connection.sync_order_statuses import sync_all_order_statuses, sync_cahnged_order_statuses
from config.setting import product as setting_product

urlpatterns = [
    path('tinymce/', include('tinymce.urls')),
    path('api/', include('api.urls')),

    path('admin/', admin.site.urls),
    path('', home.home, name='home'),
    path('home', home.home, name='home'),

    path('change_color', home.change_color, name='change_color'),

    path('development/', home.development, name='development'),

    path('sync_all_order_statuses/<str:code>', sync_all_order_statuses),
    path('sync_changed_order_statuses/<str:code>/<int:site_id>', sync_cahnged_order_statuses),
    path('order/print/unshipped-orders', print_unshipped_orders.order_print_unshipped_orders,
         name="order_print_unshipped_orders"),
    path('order/print/unshipped-orders/api', print_unshipped_orders.print_unshipped_orders_api,
         name="print_unshipped_orders_api"),


    path('stream/', include('config.stream.urls')),
    path('orders/', include('config.orders.urls')),
    path('operator-app/', include('config.operator_app.urls')),
    path('operator/', include('config.operator.urls')),
    path('warehouse/', include('config.warehouse.urls')),
    path('driver/', include('config.driver.urls')),
    path('driver-app/', include('config.driver_app.urls')),
    path('seller/', include('config.seller.urls')),
    path('seller-app/', include('config.seller_app.urls')),
    path('setting/', include('config.setting.urls')),
    path('cron-job/', include('config.cron_job.urls')),



    # admin login
    path('login-admin', login.login_user, name='admin_login'),
    path('logout', login.logout_user, name='logout'),
    # product wait region list shu ni details
    # order
    path('cash', cash_main.cash, name='cash'),

    path('cash/json-data', cash_main.cash_json_data, name='cash_json_data'),
    path('cash/filter/json-data', cash_main.cash_filter_json_data, name='cash_filter_json_data'),
    path('cash/report/json-data', cash_main.cash_report_json_data, name='cash_report_json_data'),

    path('cash/in/json-data', cash_main.cash_in_data_json, name='cash_in_data_json'),
    path('cash/out/json-data', cash_main.cash_out_data_json, name='cash_out_data_json'),
    path('cash/transfer/json-data', cash_main.cash_transfer_data_json, name='cash_transfer_data_json'),




    path('excel/list', excel.excel_files_list, name='excel_files_list'),

    path('shopkeeper/manage/list', shopkeeper_crud.shopkeeper_manage_list, name='shopkeeper_manage_list'),
    path('shopkeeper/manage/create', shopkeeper_crud.shopkeeper_manage_create, name='shopkeeper_manage_create'),
    path('shopkeeper/manage/edit/<int:id>', shopkeeper_crud.shopkeeper_manage_edit, name='shopkeeper_manage_edit'),

    path('report/', report.report, name='report'),
    path('report/month-by-details/', report.report_month_by_details, name='report_month_by_details'),
    path('report/create-daily-report', report.create_daily_report, name='create_daily_report'),

    path('report/big-balance', report_big_balance.report_big_balance, name='report_big_balance'),

    path('accountant/', report.accountant, name='accountant'),

    path('login/', login.login_user, name='login'),

]
urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)
admin.autodiscover()
admin.site.enable_nav_sidebar = False
admin.site.site_header = SITE_NAME
admin.site.index_title = f'Admin panel | {SITE_NAME}'
admin.site.site_title = 'Boshqaruv paneli'

handler404 = home.my_custom_page_not_found_view
handler500 = home.my_custom_error_view
handler403 = home.my_custom_permission_denied_view
handler400 = home.my_custom_bad_request_view
