
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from warehouse.models import WarehouseOperation, WareHouse, WarehousePermission
from postage.models import Postage, LogisticBranch, LogisticBranchPermission
from config.postage.permission import logistic_branch_permission_required
from user.models import User
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
@logistic_branch_permission_required('seller_return')
def postage_seller_return(request, logistic_branch_id, seller_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    logistic_branch.perms = logistic_branch.get_user_permission(request.user)
    seller = get_object_or_404(User, id=seller_id, type='6', is_active=True)

    '''
    buyerda omborda sellerga oid bo'lgan buyurtmalarni qaytarib olish kerak
    
    --Post bo'lsa
    Postage ni tekshirish kerak
    
    --post bo'lsa
    
    
    
    '''
    if request.method == 'POST':
        print(request.POST)

        action = request.POST['action']
        postage = Postage.objects.filter(action='2',
                                         from_logistic_branch=logistic_branch,
                                         from_user_status='1',
                                         to_user=seller).last()

        if not postage:
            messages.error(request, "Bunday pochta mavjud emas")
            return redirect('postage_seller_return', logistic_branch_id, seller_id)

        if postage.from_user_status != '1':
            messages.error(request, "Pochtani holatini o'zgartirish mumkun emas")
            return redirect('postage_seller_return', logistic_branch_id, seller_id)

        if postage.action == '2' and action == 'confirm':  # seller pochta topshirish tasdiqlandi
            postage.from_user_status = '2'
            postage.from_user_status_changed_at = datetime.datetime.now()
            postage.save()
            messages.success(request, "Tasdiqlandi")
            return redirect('postage_branch_seller_history', logistic_branch_id)

        if postage.action == '1' and action == 'cancel':  # seller pochta topshirish bekor qilinsa
            postage.from_user_status = '3'
            postage.from_user_status_changed_at = datetime.datetime.now()
            postage.save()
            postage_orders_id = list(PostageDetails.objects.filter(postage=postage).values_list("order_id", flat=True))
            Order.objects.filter(id__in=postage_orders_id, seller=seller).update(transaction_lock=False)
            messages.success(request, "Bekor qilindi")
            return redirect('postage_branch_seller_history', logistic_branch_id)


    return render(request, 'postage/branch/seller/return.html', {
        "logistic_branch": logistic_branch,
        "seller": seller
    })


@login_required(login_url='/login')
@logistic_branch_permission_required('seller_input')
def postage_seller_return_api(request, logistic_branch_id, seller_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    seller = get_object_or_404(User, id=seller_id, type='6', is_active=True)

    '''

    driverning tasdiqlanmagan postali borligini tekshirish
    bor bo'lsa uning postal detailslarini selected olarak vermek lazim

    hamma shu viloyatdagi va tumaniga to'g'ri keladigan buyurtmalar chiqarish kerak
    skannerlangandan keyun yonga o'tadi keyin 

    '''
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        order = Order.objects.filter(barcode=body['barcode']).first()

        try:
            with transaction.atomic():
                if not order:
                    return JsonResponse({
                        'status': 404,
                        'message': f"Bunday barcoddagi {body['barcode']} pochta mavjud emas",
                    })

                if order.status != '14':
                    return JsonResponse({
                        'status': 404,
                        'message': f"Bu pochta filealda emas holati:{order.get_status_display()}",
                    })

                if int(order.logistic_branch_id) != int(logistic_branch.id):
                    return JsonResponse({
                        'status': 404,
                        'message': f"Bu pochta bu filealda emas",
                    })

                if order.seller != seller:
                    return JsonResponse({
                        'status': 404,
                        'message': f"Bu bu pochta boshqa sellerga tegishli",
                    })

                if body['type'] == 'check':
                    if order.transaction_lock == True:
                        return JsonResponse({
                            'status': 404,
                            'message': f"Bu pochta belgilab bo'lingan",
                        })

                if int(order.logistic_branch_id) != int(logistic_branch_id):
                    return JsonResponse({
                        'status': 404,
                        'message': f"Bu pochta bu filealda emas",
                    })

                postage, create = Postage.objects.get_or_create(
                    action='2',
                    from_logistic_branch_id=logistic_branch_id,
                    from_user_status='1',
                    to_user=seller,
                    to_user_status='1',
                    defaults={'from_user': request.user}
                )

                if body['type'] == 'check':
                    PostageDetails.objects.create(
                        postage=postage,
                        order=order,
                        scan_from_user=True
                    )
                    order.transaction_lock = True
                    order.save()
                    return JsonResponse({
                        'status': 200,
                        'message': f"Muvaffaqiyatli qaytarildi",
                    })

                if body['type'] == 'cancel':
                    PostageDetails.objects.filter(postage=postage, order=order).delete()
                    order.transaction_lock = False
                    order.save()
                    return JsonResponse({
                        'status': 200,
                        'message': f"Muvaffaqiyatli qaytarildi"})
        except Exception as e:
            handle_exception(e)
            return JsonResponse({
                'status': 404,
                'message': f"Xatolik {e}"})

    orders = Order.objects.filter(status='14',
                                  seller=seller,
                                  logistic_branch_id=logistic_branch_id
                                  )
    postage = Postage.objects.filter(action='2',
                                     from_logistic_branch=logistic_branch,
                                     from_user_status='1',
                                     to_user=seller).last()
    postage_details = PostageDetails.objects.filter(postage=postage)

    statistic_order = {
        'checked_count': orders.filter(id__in=list(postage_details.values_list("order_id", flat=True))).count(),
        'unchecked_count': orders.filter(transaction_lock=False).exclude(
            id__in=list(postage_details.values_list("order_id", flat=True))).count(),
        'total_count': 0,
    }
    statistic_order['total_count'] = statistic_order['checked_count'] + statistic_order['unchecked_count']

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
        'total_order_count': postage_details.count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
    })

