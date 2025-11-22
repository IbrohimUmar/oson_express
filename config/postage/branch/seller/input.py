import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404
from config.postage.permission import logistic_branch_permission_required
import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from order.models import Order, OrderProduct
from services.handle_exception import handle_exception
from django.core.paginator import Paginator
from postage.models import Postage, LogisticBranch, PostageDetails
from user.models import User


@login_required(login_url='/login')
@logistic_branch_permission_required('seller_input')
def postage_branch_seller_input(request, logistic_branch_id, seller_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    logistic_branch.perms = logistic_branch.get_user_permission(request.user)
    seller = get_object_or_404(User, id=seller_id, type='6', is_active=True)
    '''
    sellerdan kelgan pochtalarni qabul qilib olish
    
    1.postage va logistic branch yaratulgan bo'ladi
    
    eng tepada input turadi barcode kiritadigan joy turadi
    pastda esa pochtalar ro'yxati chiqadi skannerlanganlar success
    skannerlanmaganlari hira rangda
    hammasini skannerlab bo'lingandan so'ng tasdiqlash tugmasi disabled false bo'lishi kerak
    '''
    if request.method == 'POST':
        action = request.POST.get('action', None)
        postage = Postage.objects.filter(action='1',
                                         from_user=seller,
                                         to_logistic_branch=logistic_branch,
                                         from_user_status='1').last()

        if not postage:
            messages.error(request, "Bunday pochta mavjud emas")
            return redirect('postage_branch_seller_input', logistic_branch_id, seller_id)

        if postage.from_user_status != '1':
            messages.error(request, "Pochtani holatini o'zgartirish mumkun emas")
            return redirect('postage_branch_seller_input', logistic_branch_id, seller_id)

        postage_details = PostageDetails.objects.filter(postage=postage)
        try:
            with transaction.atomic():
                if action == 'confirm':
                    # if postage_details.filter(scan_to_user=False).exists():
                    #     messages.error(request, "Iltimos hamma pochtalarni skannerlang")
                    #     return redirect('postage_branch_seller_input', logistic_branch_id, seller_id)

                    postage.from_user_status = '2'
                    postage.from_user_status_changed_at = datetime.datetime.now()

                    postage.to_user_status = '2'
                    postage.to_user = request.user
                    postage.to_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    Order.objects.filter(
                        id__in=list(postage_details.values_list('order_id', flat=True))
                    ).update(status='13', logistic_branch_id=logistic_branch_id, transaction_lock=False)

                    messages.success(request, "Tasdiqlandi")

                elif action == 'cancel':
                    print('cancelga tushdi')
                    postage.from_user_status = '3'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.to_user_status = '3'
                    postage.to_user = request.user
                    postage.to_user_status_changed_at = datetime.datetime.now()
                    postage.save()

                    Order.objects.filter(
                        id__in=list(postage_details.values_list('order_id', flat=True))
                    ).update(logistic_branch_id=None, transaction_lock=False)
                    messages.success(request, "Bekor qilindi")
                return redirect('postage_branch_seller_details', logistic_branch_id, postage.id)
        except Exception as e:
            handle_exception(e)
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('postage_branch_seller_input', logistic_branch_id, seller_id)

    return render(request, 'postage/branch/seller/input.html', {"logistic_branch": logistic_branch, "seller": seller})


@login_required(login_url='/login')
@logistic_branch_permission_required('seller_input')
def postage_branch_seller_input_api(request, logistic_branch_id, seller_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    seller = get_object_or_404(User, id=seller_id, type='6', is_active=True)

    '''
    
    '''
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().filter(barcode=body['barcode'], seller=seller).first()
                if not order:
                    return JsonResponse({
                        'status': 404,
                        'message': "Bunday barcoddagi buyurtma mavjud emas",
                    })
                if order.status != '8':
                    return JsonResponse({
                        'status': 404,
                        'message': f"Buyurtma qadoqlandi holatida emas \n Holati: {order.get_status_display()}",
                    })


                if body['type'] == 'cancel':
                    order.transaction_lock = False
                    order.logistic_branch_id = None
                    order.save()
                    PostageDetails.objects.filter(order=order, postage__action='1',
                                                  postage__from_user_status='1').delete()
                    return JsonResponse({
                        'status': 200,
                        'message': f"Qaytarildi",
                    })

                if body['type'] == 'check':
                    if order.transaction_lock == True:
                        order.update_total_input_price()
                        return JsonResponse({
                            'status': 404,
                            'message': f"Buyurtma skannerlab bo'lingan",
                        })

                    postage = Postage.objects.filter(
                        action='1',
                        from_user=seller,
                        from_user_status='1',
                        to_logistic_branch=logistic_branch
                    ).last()
                    if not postage:
                        postage = Postage.objects.create(
                            action='1',
                            from_user=seller,
                            from_user_status='1',
                            to_logistic_branch=logistic_branch,
                        )
                    PostageDetails.objects.get_or_create(
                        postage=postage,
                        order=order,
                        scan_from_user=True,
                        scan_to_user=True,
                    )
                    order.logistic_branch_id = logistic_branch_id
                    order.transaction_lock = True
                    order.save()
                    return JsonResponse({
                        'status': 200,
                        'message': f"Skannerlandi",
                    })



        except Exception as e:
            handle_exception(e)
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })


    orders = Order.objects.filter(status='8',
                                  seller=seller,
                                  # logistic_branch_id=logistic_branch_id
                                  )

    postage = Postage.objects.filter(action='1',
                                     from_user=seller,
                                     to_logistic_branch=logistic_branch,
                                     from_user_status='1',
                                     ).order_by('-id').last()

    postage_details = PostageDetails.objects.filter(postage=postage)
    statistic_order = {
        'checked_count': orders.filter(id__in=list(postage_details.values_list("order_id", flat=True))).count(),
        'unchecked_count': orders.filter(transaction_lock=False).exclude(
            id__in=list(postage_details.values_list("order_id", flat=True))).count(),
        'total_count': 0,
    }
    statistic_order['total_count'] = statistic_order['checked_count'] + statistic_order['unchecked_count']

    print(request.GET)
    order_type = request.GET.get("card_type", '1')
    if order_type == '1':
        orders = orders.filter(transaction_lock=False).exclude(
            id__in=list(postage_details.values_list("order_id", flat=True)))
    elif order_type == '2':
        orders = orders.filter(id__in=list(postage_details.values_list("order_id", flat=True)))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(orders, 20)
    page = paginator.get_page(page_number)
    order_list = []
    for obj in page.object_list:
        i = obj
        data = {"id": i.id, 'barcode': i.barcode, 'is_print': i.is_print,
                'customer_name': i.customer_name,
                'transaction_lock': obj.transaction_lock,
                # 'transaction_lock': True,
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




def get_object_name_or_none(obj):
    if obj:
        return obj.name
    return None