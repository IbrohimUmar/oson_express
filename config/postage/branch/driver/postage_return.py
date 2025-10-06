import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from config.driver.send_products_v2 import get_object_name_or_none
from order.models import OrderProduct, Order
from services.handle_exception import handle_exception
from warehouse.models import WarehouseOperation, WareHouse, WarehousePermission
from postage.models import Postage, LogisticBranch, LogisticBranchPermission, PostageDetails
from config.postage.permission import logistic_branch_permission_required

from user.models import Regions, User



@login_required(login_url='/login')
def postage_branch_driver_return(request, logistic_branch_id, postage_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    logistic_branch.perms = logistic_branch.get_user_permission(request.user)
    postage = get_object_or_404(Postage, id=postage_id)

    if request.method == 'POST':
        action = request.POST.get('action', None)
        postage_details = PostageDetails.objects.filter(postage=postage)
        try:
            with transaction.atomic():

                '''
                -agar confirm bo'lsa
                1. tekshirish kerak hammasi skannerlandimi?
                2.postage statuslarini o'zgartirishim kerak
                3. order filealda xolatiga o'zgartirish kerak trasaction lockdan olib tashlash kerak
                
                agar bekor qilinsachi
                --postageni xolatini o'zgartirish kerak
                --transaction lockdan chiqarib qo'yish kerak
                '''
                if action == 'confirm':
                    if postage_details.filter(scan_to_user=False).exists():
                        messages.error(request, "Iltimos hamma pochtalarni skannerlang")
                        return redirect('postage_branch_driver_return', logistic_branch_id, postage_id)

                    postage.to_user_status = '2'
                    postage.to_user = request.user
                    postage.to_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    Order.objects.filter(
                        id__in=list(postage_details.values_list('order_id', flat=True))
                    ).update(status='14', logistic_branch_id=logistic_branch_id, transaction_lock=False)

                    messages.success(request, "Tasdiqlandi")
                    return redirect('postage_branch_driver_details', logistic_branch_id, postage_id)


                elif action == 'cancel':
                    postage.to_user_status = '3'
                    postage.to_user = request.user
                    postage.to_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    messages.success(request, "Bekor qilindi")
                    return redirect('postage_branch_driver_details', logistic_branch_id, postage_id)

        except Exception as e:
            handle_exception(e)
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('postage_branch_driver_return', logistic_branch_id, postage_id)

    return render(request, 'postage/branch/driver/return.html', {
        "logistic_branch": logistic_branch,
        "postage": postage,
    })


@login_required(login_url='/login')
@logistic_branch_permission_required('seller_input')
def postage_branch_driver_return_api(request, logistic_branch_id, postage_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    postage = get_object_or_404(Postage, id=postage_id, from_user_status='2', to_user_status='1')

    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        try:
            with transaction.atomic():
                postage_details = PostageDetails.objects.select_for_update().filter(postage=postage, order__barcode=body['barcode']).first()
                if not postage_details:
                    return JsonResponse({
                        'status': 404,
                        'message': f"Bunday barcoddagi {body['barcode']} pochta mavjud emas",
                    })
                if body['type'] == 'check':

                    if postage_details.scan_to_user == True:
                        return JsonResponse({
                            'status': 404,
                            'message': f"Bu barcoddagi {body['barcode']} pochta kannerlab bo'lingan",
                        })
                    postage_details.scan_to_user = True
                    postage_details.save()
                    return JsonResponse({
                                        'status': 200,
                                        'message': f"Muvaffaqiyatli skannerlandi",
                                    })

                if body['type'] == 'cancel':
                    if postage_details.scan_to_user == False:
                        return JsonResponse({
                            'status': 404,
                            'message': f"Bu barcoddagi {body['barcode']} pochta skannerlanmagan xolatda",
                        })
                    postage_details.scan_to_user = False
                    postage_details.save()
                    return JsonResponse({
                                        'status': 200,
                                        'message': f"Muvaffaqiyatli qaytarildi",
                                    })
        except Exception as e:
            handle_exception(e)
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })


    postage_details = PostageDetails.objects.filter(postage=postage).order_by("-updated_at")
    statistic_order = postage_details.aggregate(
        checked_count=Count('id', filter=Q(scan_to_user=True)),
        unchecked_count=Count('id', filter=Q(scan_to_user=False)),
        total_count=Count('id')
    )

    order_type = request.GET.get("card_type", '1')
    if order_type == '1':
        postage_details = postage_details.filter(scan_to_user=False)
    elif order_type == '2':
        postage_details = postage_details.filter(scan_to_user=True)

    page_number = request.GET.get('page', 1)
    paginator = Paginator(postage_details, 20)
    page = paginator.get_page(page_number)
    order_list = []

    for obj in page.object_list:
        i = obj.order
        data = {"id": i.id, 'barcode': i.barcode, 'is_print': i.is_print,
                'customer_name': i.customer_name,
                'transaction_lock': obj.scan_to_user,
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
        'total_order_count': postage_details.count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
    })




