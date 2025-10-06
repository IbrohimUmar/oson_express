from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404, render, redirect

from user.models import User


@login_required(login_url='/login')
@permission_required('admin.seller_app_marketer_edit', login_url="/home")
def seller_app_marketer_edit(request, id):
    def get_or_null(value):
        if value:
            return value
        return 0

    marketer = get_object_or_404(User, id=id, type=4)
    if request.method == "POST":
        r = request.POST
        if len(r['payment_card']) > 16:
            return render(request, 'marketer/edit.html', {"r": request.POST,
                                                          'messages_error': "Sotuvchi karta raqami ko'pi bilan 16 xonali bo'lishi mumkun iltimos to'g'ri kiriting"})
        if len(r['password_text']) < 8:
            return render(request, 'marketer/edit.html', {"r": request.POST,
                                                          'messages_error': "Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})

        if User.objects.filter(username=int(r['username'])).exclude(id=id).exists():
            return render(request, 'marketer/edit.html', {"r": request.POST,
                                                          'messages_error': "Bu telefon raqamli foydaalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})

        marketer.username = int(r['username'])
        marketer.first_name = r['first_name']
        marketer.last_name = r['last_name']
        marketer.password = make_password(r['password_text'])
        marketer.password_text = r['password_text']
        marketer.payment_card = r['payment_card']
        marketer.is_staff = {"on": True}.get(r.get("is_active", False), False)
        marketer.is_active = {"on": True}.get(r.get("is_active", False), False)
        marketer.save()

        my_group = Group.objects.get(name='Sotuvchi Panel')
        my_group.user_set.add(marketer)
        messages.success(request, "O'zgartirildi")
        return redirect('seller_app_marketer_edit', id)
    return render(request, 'seller_app/marketer/edit.html',
                  {"marketer": marketer, 'r': marketer, 'main': True})
