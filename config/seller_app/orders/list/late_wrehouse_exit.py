from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order, OrderProduct
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator
from django.db.models import Q, F, Count

from user.models import User
import datetime
from user.models import Regions
from store.models import Product
from django.core.cache import cache
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.cache import cache

# late_warehouse_exit



@login_required(login_url='/login')
@permission_required('admin.seller_app_orders_list_late_warehouse_exit', login_url="/home")
def seller_app_orders_list_late_warehouse_exit(request):
    three_days_ago = datetime.datetime.today() - datetime.timedelta(days=2)
    orders = Order.objects.filter(status=1, created_at__lte=three_days_ago).order_by("created_at")
    drivers = User.objects.filter(type=2, is_active=True)
    regions = cache.get_or_set("regions", Regions.objects.values("id", "name"))
    products = cache.get_or_set("products", Product.objects.values("id", "name"))
    if request.GET.get("search", None):
        query = request.GET["search"]
        orders = orders.filter(
            Q(id__contains=query) | Q(customer_phone__contains=query) | Q(customer_phone2__contains=query))

    if request.GET.get("region", None) not in {None, "0"}:
        print('region')
        orders = orders.filter(customer_region_id=request.GET['region'])

    if request.GET.get("product", None) not in {None, "0"}:
        print('product')
        order_pro = set(OrderProduct.objects.filter(product_id=request.GET['product'],
                                                    order__in=orders.values_list("id", flat=True)).values_list(
            "order_id", flat=True))
        orders = orders.filter(id__in=order_pro)

    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, "seller_app/orders/list/late_warehouse_exit.html",
                  {"regions": regions, "products": products, 'page_obj': queryset, "drivers": drivers,
                   'count': orders.count})
