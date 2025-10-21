import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order

@login_required(login_url='/login')
@permission_required('admin.order_print', login_url="/home")
def order_print(request, id):
    order = Order.objects.filter(id=id).first()
    if order:
        return render(request, 'order/print.html', {"order": order})
    else:
        messages.error(request, "Bunday buyurtma topilmadi")
        return redirect("home")
