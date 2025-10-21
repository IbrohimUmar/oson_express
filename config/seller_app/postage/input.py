import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

from order.models import Order, OrderProduct
from services.handle_exception import handle_exception
from services.seller.get_seller import get_seller
from user.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator

from postage.models import Postage, LogisticBranch, PostageDetails


@login_required(login_url='/login')
@permission_required('admin.seller_app_postage_input', login_url="/home")
def seller_app_postage_input(request):
    seller = get_seller(request.user)
    '''
    yuqorida barcode kiritadigan joy
    
    va pastda hali yakunlanmagan amaliyot bo'lsa u chiqishi kerak
    unga seller tomonidan o'qitilgan  buyurtmalar ro'yxati chiqadigan qilish
    u buyurtmalarda transaction lock qilish kerak
    va hohlasa yana o'qitish yoki tasdiqlash imkoniyati
    
    
    -tasdiqlash button
    -bekor qilish button
    -barcode input
    -qadoqlanmoqdadagi buyurtmalar soniha  chiqishi
    -buyurtmalar ro'yxati tanlanganlar
     -qaytarish knopkasi qo'yish bosilganda tanlanganlardan qaytishi
     -yuborishga tayyorlar ro'yxati va tanlanganlar yashil tanlanmaganlar qizilda chiqishi kerak
         
    '''
    return redirect('seller_app_postage_history')
    # return render(request, 'seller_app/postage/input.html', {'seller': seller})

@login_required(login_url='/login')
@permission_required('admin.seller_app_postage_input', login_url="/home")
def seller_app_postage_input_api(request):
    seller = get_seller(request.user)
    '''
    jami yuborishga tayyorlar count
    jami qadoqlanmoqda count

    order list
    id, client full name barcode

    -post
    barcode


    '''

    # print(request.GET)
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().filter(barcode=body['barcode']).first()
                if not order:
                    return JsonResponse({
                        'status': 404,
                        'message': "Bunday barcoddagi buyurtma mavjud emas",
                    })

                if body['type'] == 'cancel':
                    '''
                    postal yaratilgan tasdiqlanmagan va faqat shu buyurtmani o'zi bo'lsa 
                    postalni o'chirib tashlash kerak
                    
                    postal detailsda bor yo'q ligini tekshirish kerak agar bor bo'lsa o'chirib tashlash
                    
                    buyurtmani transaction lock false qilib qo'yish
                    
                    '''
                    order.transaction_lock = False
                    order.save()
                    PostageDetails.objects.filter(order=order, postage__action='1', postage__from_user_status='1').delete()
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
                    branch = LogisticBranch.objects.filter(type='1').first()

                    postage = Postage.objects.filter(
                        action='1',
                        from_user=seller,
                        from_user_status='1',
                    ).last()
                    if not postage:
                        postage = Postage.objects.create(
                            action='1',
                            from_user=seller,
                            from_user_status='1',
                            to_logistic_branch=branch,
                        )
                    PostageDetails.objects.get_or_create(
                        postage=postage,
                        order=order,
                        scan_from_user=True,
                    )
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

    order_type = request.GET.get("card_type", '1')
    orders = Order.objects.filter(status='2', seller=seller).order_by('-updated_at')

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


    statistic_order = Order.objects.filter(seller=seller).aggregate(
        checked_ready_order_count=Count('id', filter=Q(status='2', transaction_lock=True)),
        unchecked_ready_order_count=Count('id', filter=Q(status='2', transaction_lock=False)),
        unchecked_ready_order_counta=Count('id', filter=Q(status='2')),
        being_packed_order_count=Count('id', filter=Q(status='8'))
    )
    return JsonResponse({
        'status': 200,
        'data': order_list,

        'statistic_order': statistic_order,

        'checked_ready_order_count': statistic_order['checked_ready_order_count'],
        'unchecked_ready_order_count': statistic_order['unchecked_ready_order_count'],
        'being_packed_order_count': statistic_order['being_packed_order_count'],

        'order_count': len(order_list),
        'total_order_count': orders.count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
    })



def get_object_name_or_none(obj):
    if obj:
        return obj.name
    return None