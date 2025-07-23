from asgiref.sync import async_to_sync
from django.contrib import messages
from django.shortcuts import redirect, render
from config.driver_app.permission import is_driver
from user.models import TempPayment, User, CashCategory


@is_driver
@async_to_sync
async def driver_app_payment_create(request):
    if request.method == 'POST':
        r = request.POST
        cashier = r.get("cashier", None)
        if cashier:
            cashier = User.objects.get(id=cashier)
        category, create = CashCategory.objects.get_or_create(name="Haydovchi to'lov qildi", type='1')
        TempPayment.objects.create(user=request.user, amount=r['amount'], cashier=cashier,
                                   category=category, desc=r['desc'])
        messages.success(request, "Qo'shildi")
        return redirect('driver_app_payment_history')
    return render(request, 'driver_app/payment/create.html',{})

