
from django.urls import path, include

from config.driver import send_products_v2, driver, return_products
from config.driver import daily_report as driver_daily_report

urlpatterns = [
    # products
    path('list', driver.driver_list, name='driver_list'),
    path('create', driver.driver_create, name='driver_create'),
    path('edit/<int:id>', driver.driver_edit, name='driver_edit'),

    path('details/<int:id>', driver.driver_about, name='driver_about'),

    path('report/', include("config.driver.report.urls")),

    path('warehouse/', include("config.driver.warehouse.urls")),
    
    path('send-barcode/', include("config.driver.send_barcode.urls")),

    path('order/', include("config.driver.order.urls")),

    path('payment/', include("config.driver.payment.urls")),

    path('date-by-statistic', driver.driver_date_by_statistic, name='driver_date_by_statistic'),
    path('date-by-district-statistic/<int:driver_id>', driver.driver_date_by_district_statistic, name='driver_date_by_district_statistic'),

    # path('driver-order-history/<int:id>', driver.driver_order_history, name='driver_order_history'),

    path('driver-statistic-list/', driver.driver_list_statistic, name='driver_list_statistic'),
    path('driver-temp-payment-list/', driver.driver_temp_payment_list, name='driver_temp_payment_list'),

    path('driver/daily-report/', driver_daily_report.driver_daily_report, name='driver_daily_report'),
    path('driver/daily-report/price-by', driver_daily_report.driver_daily_report_by_price,
         name='driver_daily_report_by_price'),

    path('driver/<int:driver_id>/send-products-v2/create/api', send_products_v2.print_unshipped_orders_api,
         name='driver_print_unshipped_orders_api'),
    path('driver-return-products-list/<int:id>', return_products.driver_return_products_list,
         name='driver_return_products_list'),
]