from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction, IntegrityError
from django.db.models import F
from django.shortcuts import redirect, render

from cash.models import Cash
from user.models import User, CashierUser, CashCategory
import datetime

@login_required(login_url='/login')
@permission_required('admin.driver_payment_create', login_url="/home")
def driver_payment_create(request, id):
    driver = User.objects.filter(type=2, id=id).first()
    if driver:
        cashier = CashierUser.objects.filter(user__is_active=True)
        category = CashCategory.objects.filter(id__in=[35 ,34 ,36 ,37])
        if request.method == "POST":
            print(request.POST)
            try:
                with transaction.atomic():
                    # cat, create = CashCategory.objects.get_or_create(name="Haydovchi to'lov qildi")
                    to_user = None
                    type = 2
                    if request.POST.get("to_user", None) != '0':
                        type=1
                        to_user = CashierUser.objects.get(user_id=request.POST.get("to_user", None)).user
                        CashierUser.objects.filter(user_id=request.POST['to_user']).update \
                            (balance=F("balance" ) +int(request.POST['amount']) ,updated_at=datetime.datetime.now())
                    Cash.objects.create(
                        type=type,
                        from_user=driver,
                        to_user=to_user,
                        desc=request.POST['desc'],
                        amount=request.POST['amount'],
                        responsible=request.user,
                        category_id=request.POST['category']
                    )
                    messages.success(request, "Ma'lumotlar saqlandi")
                    return redirect('driver_payment_list', driver.id)
            except IntegrityError as e:
                messages.error(request, f"Sizda hatolik mavjud {e}")
                return redirect('driver_payment_list', driver.id)
        return render(request, 'driver/payment/create.html', {"d" :driver, "cashier" :cashier, 'category' :category})
    else:
        messages.error(request, "Xato buyruq")
        return redirect('driver_list')
