from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from user.models import User

from cash.models import Cash
from user.models import CashierUser, CashCategory


from django.db import transaction, IntegrityError
from django.db.models import F
import datetime

@login_required(login_url='/login')
@permission_required('admin.operator_payment_create', login_url="/home")
def operator_payment_create(request, operator_id):
    operator = get_object_or_404(User, id=operator_id, type=3)
    cashier_users = CashierUser.objects.all()
    if request.method == 'POST':
        print(request.POST)
        r = request.POST
        try:
            with transaction.atomic():
                category = CashCategory.objects.filter(name="Operatorga to'lov qilindi").first()
                if not category:
                    category = CashCategory.objects.create(name="Operatorga to'lov qilindi")
                CashierUser.objects.filter(user_id=request.POST['from_user']).update(
                    balance=F("balance") - int(request.POST['amount']), updated_at=datetime.datetime.now())
                cash = Cash.objects.create(
                    type=2, from_user_id=r['from_user'], to_user=operator,
                    responsible=request.user, amount=r['amount'], desc=r['desc'],
                    category=category
                )
                messages.success(request, "Ma'lumotlar saqlandi")
                return redirect("operator_payment_list", operator_id)
        except IntegrityError as e:
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect("operator_payment_list", operator_id)

    return render(request, 'operator/payment/create.html', {'operator':operator, "cashier_users":cashier_users})

