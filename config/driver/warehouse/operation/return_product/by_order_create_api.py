import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from config.driver.send_products_v2 import get_object_name_or_none
from config.warehouse.services.warehouse_operation_item_details_manager import WarehouseOperationItemDetailsManager
from config.warehouse.services.warehouse_operation_item_manager import WarehouseOperationItemManager
from order.models import Order, OrderProduct
from order.services.order_warehouse_operation import OrderWarehouseOperationsService, InsufficientStockError
from user.models import User
from warehouse.models import WarehouseOperationAndOrderRelations, WarehouseOperation, WareHouse, \
    WarehouseOperationItemDetails
import datetime
from order.services.order_warehouse_operation import OrderWarehouseOperationsService


@permission_required('admin.driver_warehouse_operation_return_product_by_order_create_scanner', login_url="/home")
def driver_warehouse_operation_return_product_by_order_create_api(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    if request.method == "POST":
        try:
            with transaction.atomic():
                body = json.loads(request.body.decode('utf-8'))

                if len(body['barcode']) < 13:
                    return JsonResponse({
                        'status': 404,
                        'message': f"Barkodda xatolik",
                        'desc': f"Hato skannerlangan type {type(body['barcode'])}, val {body}",
                    })
                order = Order.objects.filter(barcode=body['barcode']).select_for_update()
                if order:
                    order = order.first()
                    if order.status != '5':
                        return JsonResponse({
                            'status': 404,
                            'message': f"Buyurtma bekor qilinmagan",
                            'desc': f"Qaytarish uchun buyurtma bekor qilinishi kerak bu buyurma holati '{order.get_status_display()}'",
                        })
                    if order.cancelled_status != '1':
                        return JsonResponse({
                            'status': 404,
                            'message': f"Buyurtma mahsulotlari haydovchi qo'lida emas",
                            'desc': f"Bu buyurtma haydovchi qo'lida emas :  '{order.get_cancelled_status_display()}'",
                        })
                    if int(order.driver_id) != driver_id:
                        return JsonResponse({
                            'status': 404,
                            'message': f"Haydovchi xato",
                            'desc': f"Bu buyurtma boshqa haydovchiga oid  haydovchi : '{order.driver.first_name} {order.driver.last_name}'",
                        })
                    order_warehouse_services = OrderWarehouseOperationsService()
                    order_warehouse_services.driver_return_product_from_driver(driver, order, request.user)
                    return JsonResponse({
                        'status': 200,
                        'message': "Belgilandi",
                    })
                else:
                    return JsonResponse({
                        'status': 404,
                        'message': "Buyurtma topilmadi",
                        'desc': "Bunday barcod raqamlik buyurtma topilmadi",
                    })
        except InsufficientStockError as e:
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
                'desc': f"Omborga mahsulot qo'shishda xatolik",
            })
        except Exception as e:
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })
    orders = []
    # warehouse_operations = WarehouseOperation.objects.filter(from_warehouse_status="1", to_warehouse_responsible=driver).last()
    warehouse_operations = WarehouseOperation.objects.filter(action="4", to_warehouse_id=1, from_warehouse_status="1", from_warehouse_responsible=driver).last()
    if warehouse_operations:
        orders_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation=warehouse_operations).values_list("order_id", flat=True))
        orders = Order.objects.filter(status=5, driver_id=driver_id,id__in=orders_id).order_by('-updated_at')
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

            if p.type == '1':
                if p.product_variable:
                    product_list.append({"type":p.product_type,"product_name":p.product.name, "color":get_object_name_or_none(p.product_variable.color), "measure_item":get_object_name_or_none(p.product_variable.measure_item), 'price':p.price_uzs, 'amount':p.total_quantity})
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
                    {"type":p.product_type,"product_name": p.product.name, "color": '',
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
        # 'order_count': 0,
        'total_order_count': len(orders),
        # 'total_order_count':0,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
    })
