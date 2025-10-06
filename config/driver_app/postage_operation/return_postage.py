import json
import datetime
from asgiref.sync import async_to_sync
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from config.driver_app.permission import is_driver
from config.postage.branch.seller.input import get_object_name_or_none
from order.models import OrderProduct, Order
from services.handle_exception import handle_exception
from warehouse.models import WarehouseOperation
from postage.models import Postage, PostageDetails, LogisticBranch
from django.db.models import Q, Count


@is_driver
def driver_app_postage_operation_return(request):
    driver = request.user
    logistic_branch = LogisticBranch.objects.filter(type='1').first()

    '''
    qo'lidagi bekor qilindilarni qaytarish sahifasi
    kirganda hali tasdiqlanmagan qaytarish qaytarib beriladi
    yoki create qilinadi

    barcode input
    buyurtmalar ro'yxati - skannerlanmaganlari
    buyurtmalar ro'yxati - skannerlanganlari
    '''

    if request.method == 'POST':
        action = request.POST.get('action', None)
        try:
            with transaction.atomic():
                postage = Postage.objects.filter(from_user=driver, action='4', from_user_status='1',
                                                 to_user_status='1').select_for_update().first()

                if action == 'confirm':
                    postage.from_user_status = '2'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    messages.success(request, "Tasdiqlandi")
                    return redirect('driver_app_postage_operation_history')


                elif action == 'cancel':
                    postage.from_user_status = '3'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()

                    orders = postage.postage_orders
                    orders.update(updated_at=datetime.datetime.today(),
                                  transaction_lock=False)
                    messages.success(request, "Bekor qilindi")
                    return redirect('driver_app_postage_operation_history')

        except Exception as e:
            handle_exception(e)
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('driver_app_postage_operation_history')

    return render(request, 'driver_app/postage_operation/return.html', {
        "logistic_branch":logistic_branch
    })


@is_driver
def driver_app_postage_operation_return_api(request):
    driver = request.user
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        order = Order.objects.filter(barcode=body['barcode'], driver=driver, status='5').first()
        logistic_branch_main = LogisticBranch.objects.filter(type='1').first()
        try:
            with transaction.atomic():
                if not order:
                    return JsonResponse({
                            'status': 404,
                            'message': f"Bunday barcoddagi {body['barcode']} pochta mavjud emas",
                        })

                if order.status != '5':
                    return JsonResponse({
                            'status': 404,
                            'message': f"Bu pochta holati bekor qilindi emas -> holati:{order.get_status_display()}",
                        })

                if body['type'] == 'check':
                    if order.transaction_lock == True:
                        return JsonResponse({
                            'status': 404,
                            'message': f"Bu pochta belgilab bo'lingan",
                        })

                postage, create = Postage.objects.get_or_create(
                    action='4',
                    from_user=driver,
                    from_user_status='1',

                    to_logistic_branch=logistic_branch_main,
                    to_user_status='1',

                )

                if body['type'] == 'check':
                    PostageDetails.objects.create(
                        postage=postage,
                        order=order,
                        scan_from_user=True
                    )
                    order.transaction_lock=True
                    order.save()
                    return JsonResponse({
                                    'status': 200,
                                    'message': f"Muvaffaqiyatli qaytarildi",
                                })

                if body['type'] == 'cancel':
                    PostageDetails.objects.filter(postage=postage, order=order).delete()
                    order.transaction_lock=False
                    order.save()
                    return JsonResponse({
                        'status': 200,
                        'message': f"Muvaffaqiyatli qaytarildi"})
        except Exception as e:
            handle_exception(e)
            return JsonResponse({
                'status': 404,
                'message': f"Xatolik {e}"})



    orders = Order.objects.filter(driver=request.user, status="5")

    statistic_order = {
        'checked_count': orders.filter(transaction_lock=True).count(),
        'unchecked_count':orders.filter(transaction_lock=False).count(),
        'total_count':0,
    }
    statistic_order['total_count'] = statistic_order['checked_count'] + statistic_order['unchecked_count']

    order_type = request.GET.get("card_type", '1')
    if order_type == '1':
        orders = orders.filter(transaction_lock=False)

    elif order_type == '2':
        orders = orders.filter(transaction_lock=True)

    page_number = request.GET.get('page', 1)
    paginator = Paginator(orders, 20)
    page = paginator.get_page(page_number)
    order_list = []
    for i in page.object_list:
        data = {"id": i.id, 'barcode': i.barcode, 'is_print': i.is_print,
                'customer_name': i.customer_name,
                'transaction_lock': i.transaction_lock,
                'is_there_previous_order': i.is_there_previous_order.id if i.is_there_previous_order is not None else None,
                'customer_phone': i.customer_phone, 'customer_phone2': i.customer_phone2,
                'customer_region': i.customer_region.name if i.customer_region is not None else '',
                'customer_district': i.customer_district.name if i.customer_district is not None else '',
                'customer_street': i.customer_street,
                "total_price": i.order_products_total_price_uzs}

        product_list = []
        for p in i.order_products:

            if p.product_type == '1':
                if p.product_variable:
                    product_list.append({"type": p.product_type, "product_name": p.product.name,
                                         "color": get_object_name_or_none(p.product_variable.color),
                                         "measure_item": get_object_name_or_none(p.product_variable.measure_item),
                                         'price': p.price_uzs, 'amount': p.total_quantity})
                else:
                    product_list.append(
                        {"type": p.product_type, "product_name": p.product.name, "color": '',
                         "measure_item": '', 'price': p.price_uzs,
                         'amount': p.total_quantity})

            else:
                collection_items = [{"product_name": item.product.name,
                                     "color": get_object_name_or_none(item.product_variable.color),
                                     "measure_item": get_object_name_or_none(item.product_variable.measure_item)} for
                                    item in OrderProduct.objects.filter(main_order_product=p)]
                product_list.append(
                    {"type": p.type, "product_name": p.product.name, "color": '',
                     "measure_item": '', 'price': p.price_uzs,
                     'amount': p.total_quantity,
                     "collection_items": collection_items
                     })
        data['product_list'] = product_list
        order_list.append(data)

    return JsonResponse({
        'status': 200,
        'data': order_list,

        'statistic_order': statistic_order,
        'order_count': len(order_list),
        'total_order_count': orders.count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
    })

