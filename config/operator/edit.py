from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from config.permission import operator_permission_group, operator_app_permission_group
from user.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
import datetime
import calendar
from django.contrib.auth.models import Group, Permission


@login_required(login_url='/login')
@permission_required('admin.operator_edit', login_url="/home")
def operator_edit(request, id):
    def get_or_null(value):
        if value:
            return value
        return 0

    operator = get_object_or_404(User, id=id, type=3)


    if request.method == "POST":
        r = request.POST
        if len(r['password_text']) < 8:
            return render(request, 'operator/edit.html', {"r": request.POST,
                                                                              'messages_error': "Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})
        if int(r['operator_id']) != int(get_or_null(operator.operator_id)):
            if User.objects.filter(operator_id=int(r['operator_id']), is_active=True).exists():
                return render(request, 'operator/edit.html', {"r": request.POST,
                                                                                  'messages_error': "bu operator id oldin boshqa operator id raqami o'laroq kirib bo'lingan"})

        if int(r['username']) != int(operator.username):
            if User.objects.filter(username=int(r['username'])).exists():
                return render(request, 'operator/edit.html', {"r": request.POST,
                                                                                  'messages_error': "Bu telefon raqamli operator mavjud. iltimos boshqa telefon raqam kiriting"})
        operator.username = int(r['username'])
        operator.operator_id = int(r['operator_id'])
        operator.first_name = r['first_name']
        operator.last_name = r['last_name']
        operator.password = make_password(r['password_text'])
        operator.password_text = r['password_text']
        operator.payment_card = r['payment_card']
        operator.special_fee_amount = r['special_fee_amount']
        operator.is_staff = {"on": True}.get(r.get("is_active", False), False)
        operator.is_active = {"on": True}.get(r.get("is_active", False), False)
        operator.save()
        my_group = operator_app_permission_group()
        my_group.user_set.add(operator)

        advanced_perms = dict(r).get('permissions', [])
        permission = Permission.objects.filter(codename__in=advanced_perms)
        users = User.objects.get(id=id)
        if advanced_perms and permission:
            users.user_permissions.clear()
            users.user_permissions.add(*permission)
        else:
            users.user_permissions.clear()
        users.save()
        # if {"on": True}.get(r.get("target_panel", False), False):
        #     permission = Permission.objects.get(codename='operator_ads_order_panel')
        #     users = User.objects.get(id=id)
        #     users.user_permissions.add(permission)
        #     users.save()

        # else:
        #     users = User.objects.get(id=id)
        #     permission = Permission.objects.get(codename='operator_ads_order_panel')
        #     users.user_permissions.remove(permission)
        # send_order_data_other_sites()
        activate = r.get('activate_my_call', None)
        # if activate:
        #     if not users.is_registered_my_call:
        #         create_my_calls_employee(users)
        #     else:
        #         if activate == 'on':
        #             activate = True
        #         elif activate == 'off':
        #             activate = False
        #         activate_operator(users, activate)

        messages.success(request, "O'zgartirildi")
        return redirect('operator_list')
    return render(request, 'operator/edit.html',
                  {"operator": operator, 'r': operator, 'main': True})

