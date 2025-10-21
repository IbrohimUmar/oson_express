import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order
from services.seller.get_seller import get_seller


@login_required(login_url='/login')
@permission_required('admin.seller_app_order_print', login_url="/home")
def seller_app_order_print(request, id):
    seller = get_seller(request.user)
    order = Order.objects.filter(id=id, seller=seller).first()
    if order:
        if request.method == "POST":
            from config.barcode import barcode_generate
            if int(order.status) in [1, 7, 8]:
                order.barcode = barcode_generate()
                order.save()
        return render(request, 'seller_app/orders/print.html', {"order": order})
        # return render(request, 'orders/print_v2.html', {"order": order})

    else:
        return redirect("seller_app_home")
