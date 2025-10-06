from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from cash.models import UserBalanceManager, Cash
from user.models import User, CashierUser


@login_required(login_url='/login')
@permission_required('admin.seller_app_marketer_payment_details', login_url="/home")
def seller_app_marketer_payment_details(request, payment_id):
    # payment = get_object_or_404(UserBalanceManager, id=payment_id, user__type='4')
    payment = get_object_or_404(UserBalanceManager, id=payment_id)
    cash = Cash.objects.filter(model_name='UserBalanceManager', obj_id=payment_id)
    cashier_list = CashierUser.objects.filter(user__is_active=True)
    if request.method == 'POST':
        r = request.POST
        payment.payment_card = r['payment_card']
        payment.status = r['status']
        payment.amount = r['amount']
        payment.desc = r['desc']
        payment.save()
        messages.success(request, "Saqlandi")
        return redirect('seller_app_marketer_payment_details',payment_id)
    return render(request, 'seller_app/marketer/payment/details.html', {'payment': payment, 'cashier_list':cashier_list, 'cash':cash})

