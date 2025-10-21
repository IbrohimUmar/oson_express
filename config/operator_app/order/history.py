from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render

from order.models import Order, Status


@login_required(login_url='/login')
@permission_required('admin.operator_app_order_history', login_url="/home")
@async_to_sync
async def operator_app_order_history(request):
    orders = Order.objects.filter(operator=request.user).exclude(status__in=[9, 6]).order_by("-id")
    order_counts_by_status = orders.values("status").annotate(order_count=Count("id"))
    statuses_with_counts = []
    total_order_count = 0
    for s in Status:
        order_count = 0
        if s[0] not in ['9', '6']:
            for a in order_counts_by_status:
                if int(a['status']) == int(s[0]):
                    total_order_count += a['order_count']
                    order_count = a['order_count']

            statuses_with_counts.append({'id':s[0], "status_name":s[1], "order_count":order_count})
    statuses_with_counts.append({'id':'777', "status_name":"Jami", "order_count":total_order_count})
    orders = orders.order_by("-created_at")

    status = request.GET.get("status", '777')
    if status != '777':
        orders = orders.filter(status=status)

    search = request.GET.get("search", None)
    if search:
        orders = orders.filter(Q(id__contains=search) | Q(customer_phone__contains=search))

    order_object = Paginator(orders, 25)
    page_number = request.GET.get('page')
    orders_pagination = order_object.get_page(page_number)
    return render(request, 'operator_app/order/history.html', {"order": orders_pagination, 'count': orders.count(), "statuses_with_counts":statuses_with_counts})

