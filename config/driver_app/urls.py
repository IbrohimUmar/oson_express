


from django.urls import path, include
from .menu import driver_app_menu
from .profile import driver_app_profile

urlpatterns = [
    # products
    path('profile/', driver_app_profile, name="driver_app_profile"),
    #
    # path('menu/', operator_app_menu, name="operator_app_menu"),
    #
    # path('order/list', take_order.operator_app_take_order, name="operator_app_take_order"),
    # path('order/list/filter', take_order.operator_app_take_order, name="operator_app_take_order"),
    path('menu/', driver_app_menu, name="driver_app_menu"),

    # include('warehouse/',"config.driver_app.warehouse.urls")
    # include("config.driver_app.payment.urls")

    # path('warehouse/', include('config.driver_app.warehouse.urls')),
    path('report/', include('config.driver_app.report.urls')),
    path('order/', include('config.driver_app.order.urls')),
    path('warehouse-operation/', include('config.driver_app.warehouse_operation.urls')),
    path('postage/', include('config.driver_app.postage.urls')),
    path('postage-operation/', include('config.driver_app.postage_operation.urls')),
    # path('payment/', include('config.driver_app.payment.urls'))
    path('payment/', include('config.driver_app.payment.urls'))

    # path('report/details/<int:id>', details.operator_app_order_details, name="operator_app_order_details"),
    #
    # path('order/edit/<int:id>', edit.operator_app_order_edit, name="operator_app_order_edit"),
    #
    # path('order/history', history.operator_app_order_history, name="operator_app_order_history"),
    #
    # path('order/details/get-product-details-api', details.get_site_product_details_api, name="get_site_product_details_api"),
    #
    # path('report/monthly', monthly.operator_app_monthly_report, name="operator_app_monthly_report"),
    #
    # path('concourse', concource.operator_app_concourse, name="operator_app_concourse"),
    #
    # path('task/old-order-check/<str:key>', old_order_check.operator_app_old_order_check, name="operator_app_task_old_order_check"),

]