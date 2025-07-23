from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render

from cash.models import Cash
from user.models import User


@login_required(login_url='/login')
@permission_required('admin.driver_payment_list', login_url="/home")
def driver_payment_list(request, id):
    driver = User.objects.filter(type=2, id=id).first()
    if driver:
        cash = Cash.objects.filter(from_user=driver).order_by("-created_at")
        return render(request, 'driver/payment/list.html', {"d":driver, "payment":cash})
    else:
        messages.error(request, "Xato buyruq")
        return redirect('driver_list')
