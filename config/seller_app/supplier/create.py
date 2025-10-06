from django.contrib.auth.decorators import login_required, permission_required
from user.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from config.format_money import format_money


@login_required(login_url='/login')
@permission_required('admin.seller_app_supplier_create', login_url="/home")
def seller_app_supplier_create(request):
    if request.method == "POST":
        r=request.POST
        if len(r['password_text'])<8:
            return render(request, 'shopkeeper/manage/create.html', {"r": request.POST, 'messages_error':"Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})
        if User.objects.filter(username=int(r['phone'])).exists():
            return render(request, 'shopkeeper/manage/create.html', {"r": request.POST, 'messages_error':"Bu telefon raqamli foydalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})
        User.objects.create(
            seller=request.user,
            username=int(r['phone']), first_name=r['first_name'], last_name=r['last_name'],
            password=make_password(r['password_text']), password_text=r['password_text'],
            special_fee_amount=int(r['special_fee_amount']),type=5,
            is_active={"on":True}.get(r.get("is_active", False), False)
        )
        messages.success(request, "Qo'shildi")
        return redirect('shopkeeper_manage_list')
    return render(request, 'seller_app/supplier/create.html')



