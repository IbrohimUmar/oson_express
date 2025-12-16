from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from services.order.history import save_order_status_history
from order.models import Order, OrderProduct, Status
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.db import transaction, IntegrityError

from services.seller.get_seller import get_seller
from warehouse.models import WareHouseStock
from django.db.models.functions import Coalesce
from user.models import Regions, User


@login_required(login_url='/login')
@permission_required('admin.order_sold_list', login_url="/home")
def order_sold_list(request):
    orders = Order.objects.filter(status='4').order_by("-created_at")

    region = request.GET.get("region", 'None')
    if region not in ['None', '0']:
        orders = orders.filter(customer_region=region)

    seller = request.GET.get("seller", 'None')
    if seller not in ['None', '0']:
        orders = orders.filter(seller_id=seller)

    filter_query = request.GET.get("filter", None)
    if filter_query:
        orders = orders.filter(Q(id__icontains=filter_query) | Q(customer_phone__icontains=filter_query) | Q(barcode__icontains=filter_query))

    paginator = Paginator(orders, 50)
    order = paginator.get_page(int(request.GET.get("page", 1)))
    return render(request, 'order/sold_list.html', {'quary': filter_query,'page_obj': order, "order": order, 'count': orders.count(),
                                                           "statuses":Status,
                                                    "regions":Regions.objects.all(),
                                                    "sellers":User.objects.filter(type='6')

                                                          })
