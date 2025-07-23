from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from config.permission import operator_permission_group, operator_app_permission_group
from user.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission


@login_required(login_url='/login')
@permission_required('admin.operator_create', login_url="/home")
def operator_create(request):
    if request.method == "POST":
        r = request.POST
        if len(r['password_text']) < 8:
            return render(request, 'operator/create.html', {"r": request.POST,
                                                                                'messages_error': "Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})
        if User.objects.filter(operator_id=r['operator_id'], is_active=True, type=3).exists():
            return render(request, 'operator/create.html', {"r": request.POST,
                                                                                'messages_error': "bu operator id oldin boshqa operator id raqami o'laroq kirib bo'lingan"})
        if User.objects.filter(username=int(r['phone'])).exists():
            return render(request, 'operator/create.html', {"r": request.POST,
                                                                                'messages_error': "Bu telefon raqamli operator mavjud. iltimos boshqa telefon raqam kiriting"})
        operator = User.objects.create(
            username=int(r['phone']), first_name=r['first_name'], last_name=r['last_name'],
            password=make_password(r['password_text']), password_text=r['password_text'],
            special_fee_amount=int(r['special_fee_amount']), type=3,
            is_active={"on": True}.get(r.get("is_active", False), False), operator_id=int(r['operator_id']),
            is_staff=True
        )
        my_group = operator_app_permission_group()
        my_group.user_set.add(operator)
        messages.success(request, "Operator qo'shildi")
        return redirect('operator_list')
    return render(request, 'operator/create.html')

