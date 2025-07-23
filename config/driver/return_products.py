from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.db import transaction, IntegrityError
from user.models import User
from django.shortcuts import get_object_or_404
from order.models import Order, OrderProduct



# @login_required(login_url='/login')
# @permission_required('admin.driver_list', login_url="/home")
# def driver_return_products_list(request, id):
#     driver = get_object_or_404(User, id=id, type=2)
#     orders = Order.objects.filter(driver_id=id, status=5, cancelled_status=3)
#     return render(request, 'driver/return_products/list.html', 
#     {"d":driver, 'orders':orders})

from django.core.paginator import Paginator
from django.db.models import Q

@login_required(login_url='/login')
@permission_required('admin.driver_list', login_url="/home")
def driver_return_products_list(request, id):
    driver = get_object_or_404(User, id=id, type=2)
    orders = Order.objects.filter(driver_id=id,status=5, cancelled_status=3)

    search = request.GET.get("search", None)
    if search:
        orders = orders.filter(
            Q(id__contains=search) | Q(customer_phone__contains=search) | Q(customer_phone2__contains=search))
    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page', 1)
    order = paginator.get_page(page_number)
    return render(request, 'driver/return_products/list.html', 
    {"d":driver, 'page_obj':order, "count":orders.count()})


@login_required(login_url='/login')
@permission_required('admin.driver_list', login_url="/home")
def driver_return_products_create(request, id):
    driver = get_object_or_404(User, id=id, type=2)
    cancelled_orders = Order.objects.filter(driver_id=id, status=5, cancelled_status=1)
    if cancelled_orders.count() == 0:
        messages.error(request, "Atkaz mahsulotlari yo'q")
        return redirect('driver_return_products_list', id)  
    if request.method == "POST":
        r = dict(request.POST)
        try:
                with transaction.atomic():
                    Order.objects.filter(id__in=r['order_id'], cancelled_status=1, status=5).update(
                        cancelled_status=3
                    )
                    OrderProduct.objects.filter(order_id__in=r['order_id'], status=4).update(
                        status=5
                    )
                    OrderProduct.objects.filter(order_id__in=r['order_id'], status=6).update(
                        status=7
                    )
                    messages.success(request, "Ma'lumotlar saqlandi")
                    return redirect('driver_return_products_list', id)
        except IntegrityError:
                messages.error(request, "Sizda xatolik mavjud")
                return redirect('order_give_products', id)
        
    return render(request, 'driver/return_products/create.html',
                      {'d': driver, 'cancelled_orders':cancelled_orders, 'orders_id':list(cancelled_orders.values_list("id", flat=True))})
