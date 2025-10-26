import datetime
import random

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from django.db import models, IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect


from config.operator_app.permission import check_work_hours
from order.models import Order, SellerOperatorStatusDesc
from services.order.history import save_order_status_history
from services.seller.get_seller import get_seller


@login_required(login_url='/login')
@permission_required('admin.operator_app_my_order', login_url="/home")
@check_work_hours
def operator_app_my_order(request):
    seller = get_seller(request.user)
    # order = Order.objects.filter(status__in=[9, 6], driver=None, operator=request.user).order_by('-updated_at')
    order = Order.objects.filter(driver=None, operator=request.user).order_by('-updated_at')
    statistic = Order.objects.filter(status__in=[9, 6], driver=None, operator=request.user).aggregate(
        taked_new_order=models.Count("id", filter=models.Q(status=9)),
        call_back=models.Count("id", filter=models.Q(status=6)),
        total_order=models.Count("id"),
    )
    if request.method == "POST":
        try:
            with transaction.atomic():
                r = request.POST
                order = Order.objects.filter(id=r['id'], status__in=[9, 6], operator=request.user).first()
                if order:
                    if r['status_description'] == '0':
                        messages.error(request, "Iltimos izoh tanlang")
                        return redirect('operator_app_my_order')

                    status_and_desc = get_object_or_404(SellerOperatorStatusDesc, seller=seller, id=r['status_description'])
                    order.status = status_and_desc.status
                    order.operator_comment = status_and_desc
                    order.operator_note = status_and_desc.description
                    order.operator_status_changed_at = datetime.datetime.now()

                    order.save()
                    save_order_status_history(order, order.status, "Operator buyurtmani izohini o'zgartirdi", request.user,
                                              'config.operator_app.order.my_order')
                    messages.success(request, "Saqlandi")
                    return redirect('operator_app_my_order')
                messages.error(request, "Buyurtmani o'zgartirishga kech qoldingiz")
                return redirect('operator_app_my_order')
        except IntegrityError as e:
            messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
            return redirect('operator_app_my_order')

    descriptions = SellerOperatorStatusDesc.objects.filter(seller=seller)

    for d in descriptions:
        d.order_count = order.filter(operator_comment=d).count()
        print(d)

    comment = request.GET.get("comment", None)
    if comment:
        if comment == '011':
            order = order.filter(status__in=[9, 6])
        else:
            order = order.filter(operator_comment_id=int(request.GET["comment"]))
    else:
        order = order.filter(status=9)


    order_object = Paginator(order, 25)
    page_number = request.GET.get('page')
    order_pagination = order_object.get_page(page_number)
    return render(request, 'operator_app/order/my_order.html',
                  {"order": order_pagination, "statistic": statistic, "o": request.user, "descriptions": descriptions, "total_count": order.count()
                   })
