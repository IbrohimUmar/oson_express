import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from services.order.history import save_order_status_history
from user.models import User, Districts, MarkedDeliveryPrice, Regions
from order.models import Order, OrderProduct, Status
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError


@login_required(login_url='/login')
@permission_required('admin.order_details', login_url="/home")
def order_details(request, id):
    order = get_object_or_404(Order, id=id, status__in=[3, 4, 5, 6], driver__isnull=False)
    district = Districts.objects.filter(region_id=order.customer_region_id)
    order_products = OrderProduct.objects.filter(product_type__in=[1, 2], order_id=order.id)
    if request.method == 'POST':
        r = request.POST
        try:
            with transaction.atomic():
                status = r['status']
                order = Order.objects.get(id=id)
                order.customer_name = r['customer_name']
                order.customer_phone = r['customer_phone']
                order.customer_phone2 = r['customer_phone2']
                order.driver_fee = r['driver_fee']
                order.customer_district_id = r['district']
                order.customer_street = r['street']
                order.driver_is_bonus=r.get('is_bonus', False)
                order.driver_one_day_bonus = r.get('one_day_bonus', 0)
                order.driver_two_day_bonus = r.get("two_day_bonus", 0)
                order.status=status
                order.save()

                dict_r = dict(r)
                for p in range(len(dict_r['order_product_id'])):
                    OrderProduct.objects.filter(id=dict_r['order_product_id'][p]).update(
                        total_price=dict_r['order_product_price'][p])

                order.update_product_total_price()
                order.update_product_total_quantity()
                save_order_status_history(order, order.status, "Buyurtmani o'zgartirildi", request.user,
                                          'config.orders.details')
                messages.success(request, "Ma'lumotlar saqlandi")
                return redirect("order_details", id)
        except IntegrityError:
            messages.error(request, "Sizda xatolik mavjud")
            return redirect('order_list')
    return render(request, 'orders/details.html',
                  {'is_bonus': {True: 1, False: 0, None: 0}.get(order.driver_is_bonus), "o": order,
                   'district': district, 'order_products': order_products, 'd': order.driver})

