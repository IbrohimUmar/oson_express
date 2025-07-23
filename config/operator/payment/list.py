from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from user.models import User
from cash.models import Cash

@login_required(login_url='/login')
@permission_required('admin.operator_payment_list', login_url="/home")
def operator_payment_list(request, operator_id):
    operator = get_object_or_404(User, id=operator_id, type=3)
    payment_cash = Cash.objects.filter(to_user_id=operator_id).order_by("-created_at")
    return render(request, 'operator/payment/list.html', {'operator':operator, 'payment_cash':payment_cash})

