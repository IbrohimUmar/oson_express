from django.contrib.auth.decorators import login_required, permission_required
from user.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from config.format_money import format_money

@login_required(login_url='/login')
@permission_required('admin.seller_app_supplier_list', login_url="/home")
def seller_app_supplier_list(request):
    shopkeeper = User.objects.filter(type=5, seller=request.user)
    total_balance = 0
    for s in shopkeeper:
        total_balance += s.supplier_data.balance

    if request.method == "POST":
        r = dict(request.POST)
        for index, value in enumerate(r['shopkeeper_id']):
            User.objects.filter(type=5, id=value).update(special_fee_amount=r['amount'][index])
        messages.success(request, "Ma'lumotlar saqlandi")
        return redirect("shopkeeper_manage_list")
    return render(request, 'seller_app/supplier/list.html', {'shopkeeper':shopkeeper, "total_balance":format_money(total_balance)})
