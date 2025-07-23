import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from config.driver.send_products_v2 import get_object_name_or_none
from order.models import Order, OrderProduct
from order.services.order_warehouse_operation import OrderWarehouseOperationsService, InsufficientStockError
from user.models import User
from warehouse.models import WarehouseOperationAndOrderRelations, WarehouseOperation


@permission_required('admin.driver_warehouse_operation_send_product_create_scanner', login_url="/home")
def driver_warehouse_operation_send_product_create_api(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    if request.method == "POST":
        try:
            with transaction.atomic():
                body = json.loads(request.body.decode('utf-8'))

                if len(body['barcode']) < 13:
                    return JsonResponse({
                        'status': 404,
                        'message': f"Hato skannerlangan type {type(body['barcode'])}, val {body}",
                    })

                # order = Order.objects.filter(barcode=int(body['barcode']), status=8)
                order = Order.objects.select_for_update().filter(barcode=body['barcode'], status=8)
                if order:
                    order = order.first()
                    if int(order.status) == 2:
                        return JsonResponse({
                            'status': 404,
                            'message': "Buyurtma oldin belgilab bo'lingan",
                        })
                    if order.customer_region.id != driver.region_id:
                        return JsonResponse({
                            'status': 404,
                            'message': "Buyurtma viloyati haydovchi viloyatiga to'g'ri kelmaydi",
                        })
                    services = OrderWarehouseOperationsService()
                    services.driver_send_product(driver, order, request.user)
                    return JsonResponse({
                        'status': 200,
                        'message': "Buyurtma belgilab bo'lingan",
                    })


                else:
                    order = Order.objects.filter(barcode=body['barcode']).first()
                    if order:
                        driver = 'Belgilanmagan'
                        if order.driver:
                            driver = f"{order.driver.first_name} - order.driver.last_name"

                            if order.driver_id == driver_id and int(order.status) == 2:
                                return JsonResponse({
                                    'status': 404,
                                    'message': "Buyurtma oldin belgilab bo'lingan",
                                })

                        return JsonResponse({
                            'status': 404,
                            'message': f"Bu buyurtma holati {order.get_status_display()}, haydovchi - {driver}",
                        })

                    return JsonResponse({
                        'status': 404,
                        'message': "Bu barcodelik buyurtma topilmadi",
                    })
        except InsufficientStockError as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })
    orders = []
    warehouse_operations = WarehouseOperation.objects.filter(from_warehouse_status="1", to_warehouse_responsible=driver).last()
    if warehouse_operations:
        orders_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation=warehouse_operations).values_list("order_id", flat=True))
        orders = Order.objects.filter(status=2, driver_id=driver_id,id__in=orders_id).order_by('-updated_at')
        page_number = request.GET.get('page', 1)
        paginator = Paginator(orders, 20)
        page = paginator.get_page(page_number)
        order_list = []
        for i in page.object_list:
            data = {"id":i.id, 'barcode':i.barcode, 'is_print':i.is_print,
                    'customer_name':i.customer_name, 'is_there_previous_order': i.is_there_previous_order.id if i.is_there_previous_order is not None else None,
                    'customer_phone':i.customer_phone, 'customer_phone2':i.customer_phone2,
                    'customer_region':i.customer_region.name if i.customer_region is not None else '',
                    'customer_district':i.customer_district.name if i.customer_district is not None else '', 'customer_street':i.customer_street,
                  "total_price":i.order_products_total_price_uzs}

            product_list = []
            for p in i.order_products:

                if p.product_type == '1':
                    if p.product_variable:
                        product_list.append({"type":p.product_type,"product_name":p.product.name, "color": get_object_name_or_none(p.product_variable.color), "measure_item":get_object_name_or_none(p.product_variable.measure_item), 'price':p.price_uzs, 'amount':p.total_quantity})
                    else:
                        product_list.append(
                            {"type":p.product_type,"product_name": p.product.name, "color": '',
                             "measure_item": '', 'price': p.price_uzs,
                             'amount': p.total_quantity})

                else:
                    collection_items = [{"product_name":item.product.name,
                                         "color":get_object_name_or_none(item.product_variable.color),
                                         "measure_item":get_object_name_or_none(item.product_variable.measure_item)} for item in OrderProduct.objects.filter(main_order_product=p)]
                    product_list.append(
                        {"type":p.type,"product_name": p.product.name, "color": '',
                         "measure_item": '', 'price': p.price_uzs,
                         'amount': p.total_quantity,
                         "collection_items":collection_items
                         })
            data['product_list'] = product_list
            order_list.append(data)

        return JsonResponse({
            'status': 200,
            'data': order_list,
            'order_count': len(order_list),
            'total_order_count': orders.count(),
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
            'number': page.number,
            'num_pages': paginator.num_pages,
        })
    else:
        return JsonResponse({
            'status': 200,
            'data': [],
            'order_count': 0,
            'total_order_count': 0,
            'has_next': False,
            'has_previous': False,
            'number': 0,
            'num_pages': 0,
        })