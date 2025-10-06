import os

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render

from config.export_excel import export_excel_from_driver_send_product_order_details
from order.models import Order, OrderProduct
from user.models import User
from warehouse.models import WarehouseOperation, WarehouseOperationAndOrderRelations
from order.services.order_warehouse_operation import OrderWarehouseOperationsService, InsufficientStockError
import json

# @login_required(login_url='/login')
# @permission_required('admin.driver_send_products_list', login_url="/home")
# def send_products_v2_history(request, driver_id):
#     driver = get_object_or_404(User, id=driver_id, type=2)
#     warehouse_operations = WarehouseOperation.objects.filter(to_warehouse_responsible_id=driver_id)
#     paginator = Paginator(warehouse_operations, 40)
#     page_number = request.GET.get('page')
#     result = paginator.get_page(page_number)
#     return render(request, 'driver/send_products_v2/history.html',
#                   {"d": driver, 'page_obj': result, 'count': warehouse_operations.count()})
#


# @login_required(login_url='/login')
# @permission_required('admin.driver_send_products_list', login_url="/home")
# def send_products_v2_history_order_list(request, driver_id, warehouse_operation_id):
#     driver = get_object_or_404(User, id=driver_id, type=2)
#     warehouse_operations = get_object_or_404(WarehouseOperation, id=warehouse_operation_id)
#     orders_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=warehouse_operation_id).values_list("order_id", flat=True))
#     order = Order.objects.filter(id__in=orders_id)
#
#     search = request.GET.get("search", None)
#     if search:
#         order = order.filter(
#             Q(id__contains=search) | Q(customer_phone__contains=search) | Q(customer_phone2__contains=search) | Q(
#                 customer_name__contains=search))
#
#     if 'excel' in request.GET:
#         excel = export_excel_from_driver_send_product_order_details(order)
#         static_file_path = os.path.join(excel)
#         with open(static_file_path, 'rb') as file:
#             file_content = file.read()
#         response = HttpResponse(file_content, content_type='application/vnd.ms-excel')
#         response['Content-Disposition'] = 'attachment; filename="excel.xlsx"'
#         return response
#
#     paginator = Paginator(order, 40)
#     page_number = request.GET.get('page')
#     result = paginator.get_page(page_number)
#     return render(request, 'driver/send_products_v2/history_order_list.html',
#                   {"d": driver, 'queryset': result, 'count': order.count()})

from django.db.models import Sum
from django.db.models.functions import Coalesce

#
# @login_required(login_url='/login')
# @permission_required('admin.driver_send_products_list', login_url="/home")
# def send_products_v2_history_product_list(request, driver_id, warehouse_operation_id):
#     driver = get_object_or_404(User, id=driver_id, type=2)
#     warehouse_operations = get_object_or_404(WarehouseOperation, id=warehouse_operation_id)
#     warehouse_operation_item = WarehouseOperationItem.objects.filter(warehouse_operation_id=warehouse_operation_id).values("product__name","product_variable_id", "product_variable__color__name", 'product_variable__measure_item__name').annotate(
#         total_amount=Coalesce(Sum("amount"), 0)
#     )
#
#     return render(request, 'driver/send_products_v2/history_product_list.html',
#                   {"d": driver, 'warehouse_operation_item': warehouse_operation_item})



# @login_required(login_url='/login')
# @permission_required('admin.driver_send_products_list', login_url="/home")
# def send_products_v2_create_camera(request, driver_id):
#     driver = get_object_or_404(User, id=driver_id, type=2)
#     return render(request, 'driver/send_products_v2/create_camera.html',
#                   {"d": driver})
#
# @login_required(login_url='/login')
# @permission_required('admin.driver_send_products_list', login_url="/home")
# def send_products_v2_create_scanner(request, driver_id):
#     driver = get_object_or_404(User, id=driver_id, type=2)
#     return render(request, 'driver/send_products_v2/create_scanner.html',
#                   {"d": driver})
#





def get_object_name_or_none(obj):
    if obj:
        return obj.name
    return None

@permission_required('admin.driver_send_products_list', login_url="/home")
def print_unshipped_orders_api(request, driver_id):
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
                            'status': 200,
                            'message': "Buyurtma belgilandi",
                        })
                    if order.customer_region.id != driver.region_id:
                        return JsonResponse({
                            'status': 404,
                            'message': "Buyurtma viloyati haydovchi viloyatiga to'g'ri kelmaydi",
                        })
                        
                    if order.customer_district.id not in list(driver.allow_districts.values_list("id", flat=True)):
                        return JsonResponse({
                            'status': 404,
                            'message': "Buyurtma tumani haydovchi ruxsat etilgan tumaniga to'g'ri kelmaydi",
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
                                    'status': 200,
                                    'message': "Belgilandi",
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
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })
        except Exception as e:
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })
    orders = None
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

            if p.type == '1':
                if p.product_variable:
                    product_list.append({"type":p.type,"product_name":p.product.name, "color":get_object_name_or_none(p.product_variable.color), "measure_item":get_object_name_or_none(p.product_variable.measure_item), 'price':p.price_uzs, 'amount':p.ordered_amount})
                else:
                    product_list.append(
                        {"type":p.type,"product_name": p.product.name, "color": '',
                         "measure_item": '', 'price': p.price_uzs,
                         'amount': p.ordered_amount})

            else:
                collection_items = [{"product_name":item.product.name,
                                     "color":get_object_name_or_none(item.product_variable.color),
                                     "measure_item":get_object_name_or_none(item.product_variable.measure_item)} for item in OrderProduct.objects.filter(main_order_product=p)]
                product_list.append(
                    {"type":p.type,"product_name": p.product.name, "color": '',
                     "measure_item": '', 'price': p.price_uzs,
                     'amount': p.ordered_amount,
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





# @permission_required('admin.driver_send_products_list', login_url="/home")
# def print_unshipped_orders_api(request, driver_id):
#     driver = get_object_or_404(User, id=driver_id, type=2)
#     if request.method == "POST":
#         try:
#             with transaction.atomic():
#                 body = json.loads(request.body.decode('utf-8'))

#                 if len(body['barcode']) < 13:
                    
                    
#                     return JsonResponse({
#                         'status': 404,
#                         'message': f"Hato skannerlangan type {type(body['barcode'])}, val {body}",
#                     })
                    
#                 # order = Order.objects.filter(barcode=int(body['barcode']), status=8)
#                 order = Order.objects.select_for_update().filter(barcode=body['barcode'], status=8)
#                 if order: 
#                     order = order.first()
#                     if int(order.status) == 2:
#                         return JsonResponse({
#                         'status': 200,
#                         'message': "Buyurtma belgilandi",
#                     })
#                     if order.customer_region.id != driver.region_id:
#                         return JsonResponse({
#                             'status': 404,
#                             'message': "Buyurtma viloyati haydovchi viloyatiga to'g'ri kelmaydi",
#                         })
#                     services = OrderWarehouseOperationsService()
#                     services.driver_send_product(driver, order, request.user)
#                     return JsonResponse({
#                         'status': 200,
#                         'message': "Buyurtma belgilandi",
#                     })
                
                
#                 else:
#                     order = Order.objects.filter(barcode=body['barcode']).first()
#                     if order:
#                         driver = 'Belgilanmagan'
#                         if order.driver:
#                             driver = f"{order.driver.first_name} - order.driver.last_name"
                        
#                             if order.driver_id == driver_id and int(order.status) == 2:
#                                 return JsonResponse({
#                                     'status': 200,
#                                     'message': "Belgilandi",
#                                 })
                        
                        
                        
#                         return JsonResponse({
#                             'status': 404,
#                             'message': f"Bu buyurtma holati {order.get_status_display()}, haydovchi - {driver}",
#                         })
                    
                    
#                     return JsonResponse({
#                         'status': 404,
#                         'message': "Bu barcodelik buyurtma topilmadi",
#                     })
#         except InsufficientStockError as e:
#             return JsonResponse({
#                 'status': 404,
#                 'message': f"{e}",
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'status': 404,
#                 'message': f"{e}",
#             })
#     orders = Order.objects.filter(status=2, driver_id=driver_id).count()
#     return JsonResponse({
#         'status': 200,
#         'order_count': orders,
#     })

