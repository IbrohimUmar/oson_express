from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order, OrderProduct
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator
from django.db.models import Q, F, Count
from django.db.models.functions import Length

from user.models import User
import datetime
from user.models import Regions
from store.models import Product
from django.core.cache import cache
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.cache import cache



@permission_required('admin.orders_list_double', login_url="/home")
def orders_list_double(request):
    duplicate_phone_orders = Order.objects.exclude(customer_phone__isnull=True).values('customer_phone').annotate(
        phone_len=Length('customer_phone'), count=Count('customer_phone', filter=Q(status__in=[1, 2, 3, 6]))).filter(
        count__gt=1, phone_len__gt=4)

    # duplicate_phone_orders = Order.objects.exclude(customer_phone__isnull=True, customer_phone__trim__gt="").values('customer_phone').annotate(count=Count('customer_phone', filter=Q(status__in=[1,2,3,6]))).filter(count__gt=1).order_by("-count")
    # duplicate_phone_orders = Order.objects.exclude(customer_phone__isnull=True, customer_phone__exact=" ", customer_phone__trim__gt="").values('customer_phone').annotate(count=Count('customer_phone', filter=Q(status__in=[1,2,3,6]))).filter(count__gt=1).order_by("-count")

    paginator = Paginator(duplicate_phone_orders, 30)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    data = []
    for q in queryset.object_list:
        # order = Order.objects.filter(Q(customer_phone=q['customer_phone']) | Q(customer_phone2=q['customer_phone']),
        #                             status__in=[1,2,3,6]).order_by("-created_at")

        order = Order.objects.filter(
            (Q(customer_phone=q['customer_phone']) | Q(customer_phone2=q['customer_phone'],
                                                       customer_phone2__isnull=False)),
            status__in=[1, 2, 3, 6]
        ).order_by("-created_at")
        data.append({"phone": q['customer_phone'], 'count': q['count'], "queryset": order})

    if request.method == 'POST':
        d = dict(request.POST)
        checked_orders = d.get("checked_order", None)
        if checked_orders == None:
            messages.error(request, "Buyurtma belgilang")
            return redirect('double_order_list')
        print(request.POST['checked_order'])
        Order.objects.filter(status=1, id__in=checked_orders).update(status=0, responsible=request.user,
                                                                     delete_desc="duble buyurtma")
        messages.success(request, "O'chirildi")
        return redirect('orders_list_double')
    return render(request, "orders/list/double.html", {'data': data, 'queryset': queryset})
