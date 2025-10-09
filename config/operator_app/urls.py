
from django.urls import path, include


from .profil import operator_app_profile
from .order import take_order, my_order, details, history, edit
from .report import monthly
from .concourse import concource
from .order.create import operator_app_order_create
from .task import old_order_check
from .menu import operator_app_menu

urlpatterns = [
    # products
    path('profile/', operator_app_profile, name="operator_app_profile"),

    path('menu/', operator_app_menu, name="operator_app_menu"),

    path('order/take-order', take_order.operator_app_take_order, name="operator_app_take_order"),
    path('order/my-order', my_order.operator_app_my_order, name="operator_app_my_order"),
    path('order/details/<int:id>', details.operator_app_order_details, name="operator_app_order_details"),
    path('order/edit/<int:id>', edit.operator_app_order_edit, name="operator_app_order_edit"),
    path('order/create/', operator_app_order_create, name="operator_app_order_create"),

    path('order/history', history.operator_app_order_history, name="operator_app_order_history"),

    path('report/monthly', monthly.operator_app_monthly_report, name="operator_app_monthly_report"),

    path('concourse', concource.operator_app_concourse, name="operator_app_concourse"),

    path('task/old-order-check/<str:key>', old_order_check.operator_app_old_order_check, name="operator_app_task_old_order_check"),

]