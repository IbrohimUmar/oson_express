from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from order.models import Order, DefectiveOrderDriverFee, OrderProduct


@login_required(login_url='/login/')
def driver_app_order_list_api(request):
    orders = Order.objects.filter(driver_id=request.user.id).order_by("driver_shipping_start_date")
    status = int(request.GET.get('status', 3))
    if status == 55:
            orders = orders.filter(status=5, cancelled_status="1")
    elif status == 555:
            orders = orders.filter(status=5, cancelled_status="3")
    elif status == 5555:
            orders = orders.filter(status=5, cancelled_status="2")
    else:
            orders = orders.filter(status=status)

    search_terms = request.GET.get("search", None)
    if search_terms:
        orders = orders.filter(
            Q(id__contains=search_terms) | Q(customer_phone__contains=search_terms) | Q(customer_phone2__contains=search_terms))

    district = request.GET.get("district", '0')
    if district != '0':
        orders = orders.filter(customer_district_id=district)


    def get_not_none_value(value):
        if value:
            return value
        else:
            return ''

    def get_not_none_operator_username(value):
        if value:
            return value.username
        else:
            return ''

    def defective_order_details(exchange_order, defective_sold_order):
        if defective_sold_order:
            defective_check = DefectiveOrderDriverFee.objects.filter(exchange_order=exchange_order).first()
            if defective_check:
                return {"defective_sold_order":defective_check.defective_sold_order_id, 'driver_fee':defective_check.driver_fee}
            return ''
        else:
            return ''

    page_number = request.GET.get('page', 1)
    order_length = request.GET.get('order_length', 20)
    paginator = Paginator(orders, order_length)
    page = paginator.get_page(page_number)
    order_list = []

    for r in page.object_list:
        order_list.append(
            {
                'id': r.id, 'barcode':r.barcode,'customer_name': r.customer_name, 'customer_phone': r.customer_phone,
                'customer_phone2': r.customer_phone2,
                'customer_street': r.customer_street, 'customer_district': r.customer_district.name,
                'operator': get_not_none_operator_username(r.operator), 'status': r.status,
                'status_name': r.get_status_display(),
                'order_date': r.order_date.strftime(("%Y-%m-%d")),
                'delivered_date': r.delivered_date.strftime(("%Y-%m-%d")),
                'driver_fee': r.driver_fee, 'driver_is_bonus': {True: 1, False: 0}.get(r.driver_is_bonus),
                'bonus': r.bonus,
                'products': list(
                    OrderProduct.objects.filter(order_id=r.id, type__in=[1, 2]).values('product__name', 'ordered_amount', 'price')),
                'order_products_total_ordered_amount': r.order_products_total_ordered_amount,
                'order_products_total_price': r.order_products_total_price,
                'is_delivered_date_over': {True: 1, False: 0}.get(r.is_delivered_date_over),
                'operator_note': get_not_none_value(r.operator_note),
                'cancelled_status': r.get_cancelled_status_display(),
                # "defective_product_order": 1,
                "defective_product_order": get_not_none_value(r.defective_product_order_id),
                "defective_order_details": defective_order_details(r, r.defective_product_order_id) if r.defective_product_order is not None else '',
                # "defective_order_details": {"defective_sold_order":r.id, 'driver_fee':10000},
                # "defective_order_details": '',
            })
    return JsonResponse({
        'status':200,
        'data': order_list,
        # 'data': json.dumps(order_list),
        'order_count': len(order_list),
        'total_order_count': orders.count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
    })

