from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from store.models import Product
from order.models import SellerStream, Order, Status
from django.db.models import Q

from cash.models import UserBalanceManager
MINIMAL_PAYMENT = 40000
from django.contrib import messages
from cash.models import UserBalanceManager
@login_required(login_url='/login')
@permission_required('admin.seller_app_payment_create', login_url="/home")
def seller_app_payment_create(request):
    minimal_pay = MINIMAL_PAYMENT
    if request.method == 'POST':
        try:
            amount = int(request.POST["amount"])
            payment_card = int(request.POST['payment_card'].replace(" ", ""))
        except ValueError:
            messages.warning(request, "iltimos raqam kiriting")
            return redirect("seller_app_payment_create")

        user_balance = int(request.user.seller_data.balance)
        if MINIMAL_PAYMENT > amount:
            messages.warning(request, f"Kamida {MINIMAL_PAYMENT} so'm yechishingiz mumkin")
            return redirect("seller_app_payment_create")

        if user_balance < amount:
            messages.error(request, 'Hisobingizda yetarli mablag\' mavjud emas')
            return redirect("seller_app_payment_create")

        if 2 <= UserBalanceManager.objects.filter(type='1', status='1', user=request.user).count():
            messages.error(request, "Kechirasiz sizda 2 ta to'lov bajarilganidan keyin so'rov yuborishingiz mumkin")
            return redirect("seller_app_payment_create")
        UserBalanceManager.objects.create(
            type='1',
            user=request.user,
            payment_card=payment_card,
            amount=amount
        )
        user = request.user
        user.payment_card=payment_card
        user.save()
        messages.success(request, "So'rov yuborildi")
        return redirect("seller_app_payment_list")

    return render(request, 'seller_app/payment/create.html', {'minimal_pay':minimal_pay})
