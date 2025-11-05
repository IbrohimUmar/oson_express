from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from cash.models import Cash
from config.cash.crud import check_paid_orders
from order.models import Order, CashOrderRelation
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.db.models.functions import Coalesce
from django.db.models import Sum, F, Q

from services.handle_exception import handle_exception


@login_required(login_url='/login')
@permission_required('cash.cash_list', login_url="/home")
def cash_details(request, id):
    cash = get_object_or_404(Cash, id=id)
    cash_order_relation = CashOrderRelation.objects.filter(cash_id=id, amount__gt=0).order_by("created_at")



    # Order.objects.filter(id=63).update(total_driver_payment_paid_at=F("created_at"))
    #
    # Cash.objects.all().delete()
    # CashOrderRelation.objects.all().delete()
    # Order.objects.filter(status='4').update(total_driver_payment_status='1', total_driver_payment_paid_at=None, total_driver_payment=0)
    # from user.models import CashierUser
    # CashierUser.objects.all().update(balance=0)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                check_paid_orders(cash.from_user.id)
                messages.success(request, "Taqsimlandi")
                return redirect("cash_details", id)
        except IntegrityError as e:
            handle_exception(e)
            return e

    print(cash_order_relation)
    cash_shared = Cash.objects.filter(obj_id=id, model_name="Cash")
    paginator = Paginator(cash_order_relation, 150)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'cash/details.html', {"cash":cash,
                                                 'page_obj': queryset,
                                                 'cash_shared': cash_shared,
                                                 'statistic': cash.get_cash_order_statistic,
                                                 'count': cash_order_relation.count()})

