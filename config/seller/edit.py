from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404, redirect

from config.permission import seller_app_permission_group
from user.models import User

@permission_required('admin.seller_edit', login_url="/")
def seller_edit(request, id):
    supplier = get_object_or_404(User, id=id)
    if request.method == 'POST':
        r = request.POST
        old_exists = User.objects.filter(username=r['username']).exclude(id=id).exists()
        if old_exists:
            messages.error(request, "Bu telefon raqamda boshqa foydalanuvchi mavjud iltimos boshqa telefon raqam kiriting")
            return redirect('seller_edit', id)
        supplier.username = r['username']
        supplier.first_name = r['first_name']
        supplier.last_name = r['last_name']
        supplier.special_fee_amount = r['special_fee_amount']
        supplier.password = make_password(r['password_text'])
        supplier.password_text = r['password_text']
        supplier.street = r['address']
        supplier.is_active = {"on": True}.get(r.get("is_active", False), False)
        supplier.save()

        my_group = seller_app_permission_group()
        my_group.user_set.add(supplier)
        messages.success(request, "Ma'lumotlar saqlandi")
        return redirect("seller_edit", id)
    return render(request, 'seller/edit.html',{'r':supplier})
