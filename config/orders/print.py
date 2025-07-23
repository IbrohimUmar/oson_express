import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order

@login_required(login_url='/login')
@permission_required('admin.order_print', login_url="/home")
def order_print(request, id):
    order = Order.objects.filter(id=id).first()
    if order:
        if request.method == "POST":
            from config.barcode import barcode_generate
            if int(order.status) in [1, 7, 8]:
                order.barcode = barcode_generate()
                order.save()
        return render(request, 'orders/print.html', {"order": order})
        # return render(request, 'orders/print_v2.html', {"order": order})

    else:
        return redirect("home")
