from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404, render, redirect

from user.models import User


@login_required(login_url='/login')
@permission_required('admin.seller_edit', login_url="/home")
def seller_edit(request, id):
    def get_or_null(value):
        if value:
            return value
        return 0

    seller = get_object_or_404(User, id=id, type=4)
    if request.method == "POST":
        r = request.POST
        if len(r['payment_card']) > 16:
            return render(request, 'seller/edit.html', {"r": request.POST,
                                                          'messages_error': "Sotuvchi karta raqami ko'pi bilan 16 xonali bo'lishi mumkun iltimos to'g'ri kiriting"})
        if len(r['password_text']) < 8:
            return render(request, 'seller/edit.html', {"r": request.POST,
                                                          'messages_error': "Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})

        if User.objects.filter(username=int(r['username'])).exclude(id=id).exists():
            return render(request, 'seller/edit.html', {"r": request.POST,
                                                          'messages_error': "Bu telefon raqamli foydaalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})

        seller.username = int(r['username'])
        seller.first_name = r['first_name']
        seller.last_name = r['last_name']
        seller.password = make_password(r['password_text'])
        seller.password_text = r['password_text']
        seller.payment_card = r['payment_card']
        seller.is_staff = {"on": True}.get(r.get("is_active", False), False)
        seller.is_active = {"on": True}.get(r.get("is_active", False), False)
        seller.save()

        my_group = Group.objects.get(name='Sotuvchi Panel')
        my_group.user_set.add(seller)
        messages.success(request, "O'zgartirildi")
        return redirect('seller_edit', id)
    return render(request, 'seller/edit.html',
                  {"seller": seller, 'r': seller, 'main': True})
