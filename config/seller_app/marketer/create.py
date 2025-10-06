from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction

from config.permission import marketer_app_permission_group
from services.handle_exception import handle_exception
from user.models import User


@login_required(login_url='/login')
@permission_required('admin.seller_app_marketer_create', login_url="/home")
def seller_app_marketer_create(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                r = request.POST
                if len(r['payment_card']) > 16:
                    return render(request, 'marketer/create.html', {"r": request.POST,
                                                                                        'messages_error': "Marketingchi karta raqami ko'pi bilan 16 xonali bo'lishi mumkun iltimos to'g'ri kiriting"})
                if len(r['password_text']) < 8:
                    return render(request, 'marketer/create.html', {"r": request.POST,
                                                                                        'messages_error': "Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})

                if User.objects.filter(username=int(r['phone'])).exists():
                    return render(request, 'marketer/create.html', {"r": request.POST,
                                                                                        'messages_error': "Bu telefon raqamli foydaalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})
                marketer = User.objects.create(
                    seller=request.user,
                    username=int(r['phone']),
                    first_name=r['first_name'],
                    last_name=r['last_name'],
                    password=make_password(r['password_text']), password_text=r['password_text'],
                    type=4,
                    is_active={"on": True}.get(r.get("is_active", False), False),
                    payment_card=r['payment_card']
                )

                my_group = marketer_app_permission_group()
                my_group.user_set.add(marketer)
                messages.success(request, "Marketingchi qo'shildi")
                return redirect('seller_app_marketer_list')

        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Muammo yuzaga keldi : {e}")
            return render(request, 'seller_app/marketer/create.html', {"r": request.POST,
                                                          'messages_error': f"{e}"})
    return render(request, 'seller_app/marketer/create.html')

