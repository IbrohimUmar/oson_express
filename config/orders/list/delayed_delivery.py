from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order, OrderProduct
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator
from django.db.models import Q, F, Count
from user.models import User
import datetime


@login_required(login_url='/login')
@permission_required('admin.orders_list_delayed_delivery', login_url="/home")
def orders_list_delayed_delivery(request):
    three_days_ago = datetime.datetime.today() - datetime.timedelta(days=3)
    orders = Order.objects.filter(Q(status=3) | Q(status=6), driver_shipping_start_date__lte=three_days_ago).order_by(
        "driver_shipping_start_date")
    drivers = User.objects.filter(type=2, is_active=True)
    if request.GET.get("search", None):
        query = request.GET["search"]
        orders = orders.filter(
            Q(id__contains=query) | Q(customer_phone__contains=query) | Q(customer_phone2__contains=query))

    if request.GET.get("driver", None) not in {None, "0"}:
        orders = orders.filter(driver_id=request.GET['driver'])
    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, "orders/list/delayed_delivery.html",
                  {'page_obj': queryset, "drivers": drivers, 'count': orders.count})

