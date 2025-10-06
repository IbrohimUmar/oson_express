from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
# from config.orders.other import copy_order
from order.models import Order, OrderProduct
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator
from django.db.models import Q, F, Count

from services.seller.get_seller import get_seller
from user.models import User
import datetime
from user.models import Regions
from store.models import Product
from django.core.cache import cache
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.cache import cache


PAGINATION_LENGTH = 50

def copy_order(order, operator):
    new_order = Order.objects.create(
        is_site_change=False,
        site_order_id=order.site_order_id,
        site=order.site,
        operator=operator,
        operator_fee=operator.special_fee_amount,
        status=1,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_phone2=order.customer_phone2,
        customer_region=order.customer_region,
        customer_district=order.customer_district,
        customer_street=order.customer_street,
        seller_fee=order.seller_fee,

        driver_is_bonus=order.driver_is_bonus,
        driver_one_day_bonus=order.driver_one_day_bonus,
        driver_two_day_bonus=order.driver_two_day_bonus,
        driver_bonus_amount_won=order.driver_bonus_amount_won,
        order_date=order.order_date,
        delivered_date=order.delivered_date,
    )
    order_product = OrderProduct.objects.filter(order_id=order.id, status__in=[1, 4, 5])
    old = [OrderProduct(order=new_order, status=1, product=i.product, product_item=i.product_item,
                        ordered_amount=i.ordered_amount,
                        amount=i.amount, price=i.price, input_price=i.input_price
                        ) for i in order_product]
    OrderProduct.objects.bulk_create(old)
    return new_order


@permission_required('admin.seller_app_order_list_canceled', login_url="/home")
def seller_app_orders_list_canceled(request):
    seller = get_seller(request.user)
    list_order = Order.objects.filter(status=5, seller=seller)
    regions = request.session.get("regions", Regions.objects.all())

    is_order_copy = request.GET.get("order_copy", None)
    if is_order_copy:
        params = request.GET.copy()
        if 'order_copy' in params:
            del params['order_copy']

        url = request.path + '?' + params.urlencode()
        order = Order.objects.filter(status=5, cancelled_status__in=[2, 3], id=is_order_copy).first()
        if order:
            try:
                with transaction.atomic():
                    raise IntegrityError
                    # order_new = copy_order(order, request.user)
                    # order.site_order_id = None
                    # order.operator_note = f"Mijoz buyurtmani oladigan bo'ldi. shuning uchun bu buyurtmadan nusxa olindi buyurtma id:{order_new.id}"
                    # order.save()
                    messages.success(request, f"Buyurtmani nusxalab yangiga o'tkazildi Id:{order_new.id}")
                    return redirect(url)
            except IntegrityError:
                messages.error(request, "Nusxalashda xatolik yuzberdi")
                return redirect(url)

        messages.warning(request, "Ushbu buyurma o'zgartirib bo'lingan")
        return redirect(url)

    if request.GET.get("search", None):
        query = request.GET["search"]
        list_order = list_order.filter(
            Q(id__contains=query) | Q(customer_phone__contains=query) | Q(driver__username=query))

    if request.GET.get("from_date", None) and request.GET.get("to_date", None):
        list_order = list_order.filter(updated_at__date__range=(request.GET['from_date'], request.GET['to_date']))

    if request.GET.get("region", None) not in {None, "0"}:
        list_order = list_order.filter(customer_region_id=request.GET['region'])

    paginator = Paginator(list_order.order_by("-updated_at"), PAGINATION_LENGTH)
    page_number = request.GET.get('page')
    order = paginator.get_page(page_number)
    return render(request, "seller_app/orders/list/canceled.html",
                  {'page_obj': order, 'regions': regions, "list_order": order, 'count': list_order.count()})

