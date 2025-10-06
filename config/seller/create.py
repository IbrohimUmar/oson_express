from django.contrib.auth.decorators import permission_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect

from config.permission import seller_app_permission_group
from services.handle_exception import handle_exception
from user.models import User, CashierUser
from django.contrib import messages
from warehouse.models import WareHouse, WarehousePermission
from django.db import transaction


def seller_create_warehouse(user):
    main_warehouse = WareHouse.objects.create(type='1', responsible=user)
    defective_warehouse = WareHouse.objects.create(type='2', responsible=user)
    confirm_warehouse = WareHouse.objects.create(type='3', responsible=user)
    WarehousePermission.objects.create(
        warehouse=main_warehouse,
        user=user,
        input_product=True,
        transit_product=True,
        operation_history=True,
        operation_history_details=True,
        residue=True,
    )
    WarehousePermission.objects.create(
        warehouse=defective_warehouse,
        user=user,
        input_product=True,
        transit_product=True,
        operation_history=True,
        operation_history_details=True,
        residue=True,
    )
    WarehousePermission.objects.create(
        warehouse=confirm_warehouse,
        user=user,
        input_product=True,
        transit_product=True,
        operation_history=True,
        operation_history_details=True,
        residue=True,
    )


@permission_required('admin.seller_create', login_url="/")
def seller_create(request):
    if request.method == 'POST':
        r = request.POST
        if User.objects.filter(username=r['username']).exists():
            return render(request, 'supplier/create.html', {
                'r': r,
                'messages_error': "Bu telefon raqamda boshqa foydalanuvchi mavjud. Iltimos, boshqa telefon raqam kiriting."
            })

        try:
            with transaction.atomic():
                user = User.objects.create(
                    username=r['username'],
                    first_name=r['first_name'],
                    last_name=r['last_name'],
                    special_fee_amount=r['special_fee_amount'],
                    password=make_password(r['password_text']),
                    password_text=r['password_text'],
                    street=r['address'],
                    type='6',
                    is_active={"on": True}.get(r.get("is_active", False), False)
                )

                # Kullanıcı için depo oluştur
                seller_create_warehouse(user)
                CashierUser.objects.create(user=user,
                                           balance=0)
                my_group = seller_app_permission_group()
                my_group.user_set.add(user)
                messages.success(request, "Ma'lumotlar saqlandi")
                return redirect("seller_list")

        except Exception as e:
            handle_exception(e)
            # Hata oluşursa rollback olur
            return render(request, 'seller/create.html', {
                'r': r,
                'messages_error': f"Xatolik yuz berdi: {str(e)}"
            })

    return render(request, 'seller/create.html')
