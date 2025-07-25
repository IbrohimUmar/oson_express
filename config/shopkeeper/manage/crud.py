from django.contrib.auth.decorators import login_required, permission_required
from user.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from config.format_money import format_money

@login_required(login_url='/login')
@permission_required('admin.shopkeeper_manage_list', login_url="/home")
def shopkeeper_manage_list(request):
    shopkeeper = User.objects.filter(type=5)
    total_balance = 0
    for s in shopkeeper:
        total_balance += s.shopkeeper_data.balance

        # balance = s.shopkeeper_data.balance
        # if balance >= 0:
        #     total_balance -= balance
        # else:
        #     total_balance += balance
            
            
            
    if request.method == "POST":
        r = dict(request.POST)
        for index, value in enumerate(r['shopkeeper_id']):
            User.objects.filter(type=5, id=value).update(special_fee_amount=r['amount'][index])
        messages.success(request, "Ma'lumotlar saqlandi")
        return redirect("shopkeeper_manage_list")
    return render(request, 'shopkeeper/manage/list.html', {'shopkeeper':shopkeeper, "total_balance":format_money(total_balance)})


@login_required(login_url='/login')
@permission_required('admin.shopkeeper_manage_list', login_url="/home")
def shopkeeper_manage_create(request):
    if request.method == "POST":
        r=request.POST
        if len(r['password_text'])<8:
            return render(request, 'shopkeeper/manage/create.html', {"r": request.POST, 'messages_error':"Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})
        if User.objects.filter(username=int(r['phone'])).exists():
            return render(request, 'shopkeeper/manage/create.html', {"r": request.POST, 'messages_error':"Bu telefon raqamli foydalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})
        User.objects.create(
            username=int(r['phone']), first_name=r['first_name'], last_name=r['last_name'],
            password=make_password(r['password_text']), password_text=r['password_text'],
            special_fee_amount=int(r['special_fee_amount']),type=5,
            is_active={"on":True}.get(r.get("is_active", False), False)
        )
        messages.success(request, "Qo'shildi")
        return redirect('shopkeeper_manage_list')
    return render(request, 'shopkeeper/manage/create.html')






@login_required(login_url='/login')
@permission_required('admin.shopkeeper_manage_list', login_url="/home")
def shopkeeper_manage_edit(request, id):
    r = get_object_or_404(User, id=id, type=5)
    if request.method == "POST":
        r=request.POST
        if len(r['password_text'])<8:
            return render(request, 'shopkeeper/manage/edit.html', {"r": request.POST, 'messages_error':"Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})
        if User.objects.filter(username=int(r['username'])).exclude(id=id).exists():
            return render(request, 'shopkeeper/manage/edit.html', {"r": request.POST, 'messages_error':"Bu telefon raqamli foydalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})
        User.objects.filter(id=id).update(
            username=int(r['username']), first_name=r['first_name'], last_name=r['last_name'],
            password=make_password(r['password_text']), password_text=r['password_text'],
            special_fee_amount=int(r['special_fee_amount']),type=5,
            is_active={"on":True}.get(r.get("is_active", False), False)
        )
        messages.success(request, "O'zgartirildi")
        return redirect('shopkeeper_manage_list')
    return render(request, 'shopkeeper/manage/edit.html', {"r":r})


