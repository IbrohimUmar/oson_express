from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from order.models import Order, DefectiveOrderDriverFee, OrderProduct
from config.driver_app.permission import is_driver
from django.http import JsonResponse
from order.models import DefectiveOrderDriverFee
from warehouse.models import WarehouseOperation


@is_driver
def driver_app_order_api_list(request):
    # orders = Order.objects.filter(driver_id=request.user.id).order_by("driver_shipping_start_date")
    orders = Order.objects.filter(driver_id=request.user.id).order_by("-updated_at")


    warehouse_operation_id = request.GET.get("warehouse_operation_id", None)
    if warehouse_operation_id:
        warehouse_operation = get_object_or_404(WarehouseOperation, id=warehouse_operation_id)
        orders = orders.filter(id__in=warehouse_operation.relation_orders_id)

    print(request.GET)
    status = int(request.GET.get('status', 1))
    if status:
        orders = orders.filter(driver_status=status)

    search_terms = request.GET.get("search", None)
    if search_terms:
        orders = orders.filter(
            Q(barcode__contains=search_terms) |Q(id__contains=search_terms) | Q(customer_phone__contains=search_terms) | Q(customer_phone2__contains=search_terms))

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
    # order_length = request.GET.get('order_length', 1)
    paginator = Paginator(orders, order_length)
    page = paginator.get_page(page_number)
    order_list = []
    for r in page.object_list:
        order_products = OrderProduct.objects.filter(order_id=r.id, product_type__in=[1, 2])
        products = []
        for o in order_products:
            if o.product_type == '1':
                products.append({"type":1, 'product__name':o.product.name, 'price':o.total_price, 'total_quantity':o.total_quantity,
                          'color':o.product_variable.color.name if o.product_variable.color else '',
                          'measure_item':o.product_variable.measure_item.name if o.product_variable.measure_item else '',
                          })
            elif o.product_type == '2':
                products.append({"type":2, 'product__name':o.product.name, 'price':o.total_price, 'total_quantity':o.total_quantity,
                          'items':[{"product__name":i.product.name, 'color':i.product_variable.color.name if i.product_variable.color else '',
                                    'measure_item': i.product_variable.measure_item.name if i.product_variable.measure_item else '',
                                    } for i in OrderProduct.objects.filter(Q(product_variable__color__isnull=False)|Q(product_variable__measure_item__isnull=False), main_order_product=o, product_variable__isnull=False,
                                                                           )],
                          })
        order_list.append(
            {
                'id': r.id,
                'customer_name': r.customer_name, 'customer_phone': r.customer_phone,
                'barcode': r.barcode,
                'customer_phone2': r.customer_phone2,
                'customer_street': r.customer_street,
                'customer_district': r.customer_district.name,
                'operator': get_not_none_operator_username(r.operator),
                'status': r.driver_status,
                'status_name': r.get_driver_status_display(),
                'order_date': r.order_date.strftime(("%Y-%m-%d")),
                'delivered_date': r.delivered_date.strftime(("%Y-%m-%d")),
                'driver_fee': r.driver_fee, 'driver_is_bonus': {True: 1, False: 0}.get(r.driver_is_bonus),
                'bonus': r.bonus,
                'products': products,

                'total_product_quantity': r.total_product_quantity,
                'total_product_price': r.total_product_price,

                'is_delivered_date_over': {True: 1, False: 0}.get(r.is_delivered_date_over),
                'operator_note': get_not_none_value(r.operator_note),
                'cancelled_status': '1',
                "driver_status": r.driver_status,
                "defective_product_order": get_not_none_value(r.defective_product_order_id),
                "defective_order_details": defective_order_details(r, r.defective_product_order_id) if r.defective_product_order is not None else '',
                # "defective_order_details": {"defective_sold_order":r.id, 'driver_fee':10000},
                # "defective_order_details": '',
            })
        print(order_list)
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

