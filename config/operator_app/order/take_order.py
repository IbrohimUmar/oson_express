from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from django.db import models, transaction, IntegrityError
from django.shortcuts import render, redirect
from random import shuffle
import datetime
from config.operator_app.permission import check_work_hours
from order.models import Order
from services.order.history import save_order_status_history


@login_required(login_url='/login')
@permission_required('admin.operator_app_take_order', login_url="/home")
@check_work_hours
def operator_app_take_order(request):
    seller = request.user.seller
    order = Order.objects.filter(status=9, seller=seller, operator=None).order_by('id')
    statistic = Order.objects.filter(status__in=[9, 6], seller=seller).aggregate(
        new_order=models.Count("id", filter=models.Q(status=9, operator=None)),
        taked_new_order=models.Count("id", filter=models.Q(status=9, operator__isnull=False)),
        call_back=models.Count("id", filter=models.Q(status=6))
    )
    
    if 3 < int(Order.objects.filter(status=9, operator=request.user).count()):
        messages.warning(request, "Sizda yangi buyurtmalar soni 3 ta iltimos ularga aloqaga chiqing")
        return redirect("operator_app_my_order")
        
    if request.method == "POST":
        try:
            with transaction.atomic():
                order = Order.objects.filter(id=request.POST['id'], operator=None, seller=seller).update(operator=request.user, updated_at=datetime.datetime.now())
                if order:
                    order = Order.objects.get(id=request.POST['id'])
                    save_order_status_history(order, order.status, "Operator buyurtmani uziga belgiladi", request.user,
                                              'config.operator_app.order.take_order')
                    messages.success(request, "Buyurtma olindi")
                    return redirect("operator_app_take_order")

                messages.error(request, "Buyurtmani boshqa operator olib bo'lgan")
                return redirect("operator_app_take_order")
        except IntegrityError as e:
            messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
            return redirect('operator_app_take_order')

    order_object = Paginator(order, 25)
    page_number = request.GET.get('page')
    order = order_object.get_page(page_number)
    order.object_list = list(order.object_list)
    shuffle(order.object_list)
    return render(request, 'operator_app/order/take_order.html', {"order":order, "statistic":statistic})

