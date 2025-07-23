from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from config.driver_app.permission import is_driver
from order.models import Order
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from order.models import Order, DefectiveOrderDriverFee, OrderProduct

from config.driver_app.permission import is_driver
from django.db.models import F, Sum
from django.db import transaction, IntegrityError
import json
import datetime
from django.http import JsonResponse
from order.models import DefectiveOrderDriverFee
from order.services.order_warehouse_operation import InsufficientStockError

from warehouse.models import WarehouseOperationItemDetails


@login_required(login_url='/driver-login/')
@async_to_sync
@is_driver
async def driver_app_order_scanner_cancel(request):
        district = request.user.allow_districts.all()
        return render(request, 'driver_app/order/scanner_cancel.html',
                    {'district':district})



@login_required(login_url='/driver-login/')
@async_to_sync
@is_driver
async def driver_app_order_scanner_cancel_api(request):
    orders = Order.objects.filter(driver_id=request.user.id, status='5').order_by("-updated_at")

    search_terms = request.GET.get("search", None)
    if search_terms:
        orders = orders.filter(
            Q(barcode__contains=search_terms) | Q(id__contains=search_terms) | Q(
                customer_phone__contains=search_terms) | Q(customer_phone2__contains=search_terms))

    district = request.GET.get("district", '0')
    if district != '0':
        orders = orders.filter(customer_district_id=district)

    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        if len(body['barcode']) < 13:
            return JsonResponse({
                'status': 404,
                'message': f"Hato skannerlangan type {type(body['barcode'])}, val {body}",
            })

        try:
            with transaction.atomic():
                body = json.loads(request.body.decode('utf-8'))

                if len(body['barcode']) < 13:
                    return JsonResponse({
                        'status': 404,
                        'message': f"Hato skannerlangan type {type(body['barcode'])}, val {body}",
                    })
                # order = Order.objects.filter(barcode=int(body['barcode']), status=8)
                order = Order.objects.select_for_update().filter(barcode=body['barcode'], driver=request.user)
                if order:
                    order = order.first()
                    if int(order.status) == 5:
                        return JsonResponse({
                            'status': 404,
                            'message': "Buyurtma bekor qilib bo'lingan",
                        })
                    if order.status not in ['3', '6']:
                        return JsonResponse({
                            'status': 404,
                            'message': "Faqat yetkazilmoqda va qayta qo'ng'iroqdagi buyurtmalarni bekor qilishingiz mumkun",
                        })
                    order.status=5
                    order.is_site_change=False
                    order.updated_at=datetime.datetime.now()
                    order.save()
                    return JsonResponse({
                        'status': 200,
                        'message': "Buyurtma bekor qilindi",
                    })


                else:
                    return JsonResponse({
                        'status': 404,
                        'message': "Bu barcodelik buyurtma topilmadi",
                    })
        except InsufficientStockError as e:
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })
        except Exception as e:
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })
        # return JsonResponse({
        #     'status': 200,
        #     'message': "success",
        # })

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
                return {"defective_sold_order": defective_check.defective_sold_order_id,
                        'driver_fee': defective_check.driver_fee}
            return ''
        else:
            return ''

    page_number = request.GET.get('page', 1)
    order_length = request.GET.get('order_length', 20)
    paginator = Paginator(orders, order_length)
    page = paginator.get_page(page_number)
    order_list = []

    for r in page.object_list:

        order_products = OrderProduct.objects.filter(order_id=r.id, type__in=[1, 2])
        products = []

        for o in order_products:
            if o.type == '1':
                products.append(
                    {"type": 1, 'product__name': o.product.name, 'price': o.price, 'ordered_amount': o.ordered_amount,
                     'color': o.product_variable.color.name if o.product_variable.color else '',
                     'measure_item': o.product_variable.measure_item.name if o.product_variable.measure_item else '',
                     })
            elif o.type == '2':
                products.append(
                    {"type": 2, 'product__name': o.product.name, 'price': o.price, 'ordered_amount': o.ordered_amount,
                     'items': [{"product__name": i.product.name,
                                'color': i.product_variable.color.name if i.product_variable.color else '',
                                'measure_item': i.product_variable.measure_item.name if i.product_variable.measure_item else '',
                                } for i in OrderProduct.objects.filter(
                         Q(product_variable__color__isnull=False) | Q(product_variable__measure_item__isnull=False),
                         main_order_product=o, product_variable__isnull=False,
                         )],
                     })
        order_list.append(
            {
                'id': r.id, 'customer_name': r.customer_name, 'customer_phone': r.customer_phone,
                'barcode': r.barcode,
                'customer_phone2': r.customer_phone2,
                'customer_street': r.customer_street, 'customer_district': r.customer_district.name,
                'operator': get_not_none_operator_username(r.operator), 'status': r.status,
                'status_name': r.get_status_display(),
                'order_date': r.order_date.strftime(("%Y-%m-%d")),
                'delivered_date': r.delivered_date.strftime(("%Y-%m-%d")),
                'updated_at': r.updated_at.strftime(("%Y-%m-%d %H:%M")),
                'driver_fee': r.driver_fee, 'driver_is_bonus': {True: 1, False: 0}.get(r.driver_is_bonus),
                'bonus': r.bonus,
                'products': products,

                'order_products_total_ordered_amount': r.order_products_total_ordered_amount,
                'order_products_total_price': r.order_products_total_price,
                'is_delivered_date_over': {True: 1, False: 0}.get(r.is_delivered_date_over),
                'operator_note': get_not_none_value(r.operator_note),
                # 'cancelled_status': r.get_cancelled_status_display(),
                'cancelled_status': '1',
                "payment_status": r.payment_status,
                "payment_status_name": r.get_payment_status_display(),
                "defective_product_order": get_not_none_value(r.defective_product_order_id),
                "defective_order_details": defective_order_details(r,
                                                                   r.defective_product_order_id) if r.defective_product_order is not None else '',
                # "defective_order_details": {"defective_sold_order":r.id, 'driver_fee':10000},
                # "defective_order_details": '',
            })
    return JsonResponse({
        'status': 200,
        'data': order_list,
        # 'data': json.dumps(order_list),
        'order_count': len(order_list),
        'total_order_count': orders.count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
    })
