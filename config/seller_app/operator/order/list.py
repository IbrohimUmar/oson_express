import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from order.models import Order
from services.seller.get_seller import get_seller
from user.models import User
from cash.models import Cash
from order.models import Status

@login_required(login_url='/login')
@permission_required('admin.seller_app_operator_order_list', login_url="/home")
def seller_app_operator_order_list(request):
    seller = get_seller(request.user)
    # orders = Order.objects.filter(seller=seller)
    orders = Order.objects.filter(seller=seller)
    status = request.GET.get("status", 'None')
    if status != 'None':
        if status == '99':
            orders = orders.filter(status=9, operator__isnull=False)
        else:
            orders = orders.filter(status=status)


    operator_id = request.GET.get("operator_id", '0')
    if operator_id != '0':
        orders = orders.filter(operator_id=operator_id)

    filter_query = request.GET.get("filter", None)
    if filter_query:
        orders = orders.filter(Q(id__icontains=filter_query) | Q(customer_phone__icontains=filter_query) | Q(barcode__icontains=filter_query))


    if request.method == 'POST':
        r = request.POST
        check_ids = request.POST.getlist('check')
        if r['action'] == '1' and r.get("select_all") == '1':
            order = orders.filter(Q(status='6')| Q(status='9', operator__isnull=True)).update(
                status='9',
                operator=None,
                updated_at=datetime.datetime.now(),
                operator_note=''
            )
            messages.success(request, "O'zgartirildi")
        elif r['action'] == '1' and r.get("select_all") == '0':
            order = orders.filter(status__in=[6, 9],
                                  id__in=check_ids).update(
                status='9',
                operator=None,
                updated_at=datetime.datetime.now(),
                operator_note=''
            )
            messages.success(request, "O'zgartirildi")

        if r['action'] == '2' and r.get("select_all") == '1':
            order = orders.filter(status='9', operator__isnull=False).update(
                status='6',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")
        elif r['action'] == '2' and r.get("select_all") == '0':
            order = orders.filter(id__in=check_ids, status=9,
                                   operator__isnull=False).update(
                status='6',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")



        if r['action'] == '4' and r.get("select_all") == '1':
            order = orders.filter(status='9').update(
                status='6',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")
        elif r['action'] == '4' and r.get("select_all") == '0':
            order = orders.filter(id__in=check_ids, status=9).update(
                status='6',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")



        if r['action'] == '3' and r.get("select_all") == '1':
            order = orders.filter(Q(status='6')| Q(status='9', operator__isnull=True)).update(
                status='9',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")
        elif r['action'] == '3' and r.get("select_all") == '0':
            order = orders.filter(status__in=[6, 9],
                                  id__in=check_ids).update(
                status='9',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")



        if r['action'] == '5' and r.get("select_all") == '1':
            order = orders.filter(status__in=[6, 9]).update(
                status='11',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")
        elif r['action'] == '5' and r.get("select_all") == '0':
            order = orders.filter(status__in=[6, 9],
                                  id__in=check_ids).update(
                status='11',
                updated_at=datetime.datetime.now(),
            )
            messages.success(request, "O'zgartirildi")



        return redirect('seller_app_operator_order_list')

    operators = User.objects.filter(seller=seller, type='3').order_by("-id")
    paginator = Paginator(orders, 50)
    orders_qs = paginator.get_page(int(request.GET.get("page", 1)))
    return render(request, 'seller_app/operator/order/list.html', {
        'page_obj': orders_qs,
        'operators': operators,
        'Status':Status,
                                                                   'count':orders.count()})

