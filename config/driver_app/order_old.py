import json
from random import random, randint
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from order.models import Order, OrderProduct
from django.db.models import Q, F
# from order.models import OrderSite
import time
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync, sync_to_async
from django.db import transaction, IntegrityError

status = {"2": True, '3': True, '4': True, '5': True, "6": True}


def get_order(user_id):
    return list(Order.objects.filter(driver_id=user_id).extra(
        select={'order_date_f': "DATE_FORMAT(order_date,'%%Y/%%m/%%d')",
                'delivery_date_f': "DATE_FORMAT(delivered_date,'%%Y/%%m/%%d')",
                'extra_phone': "IFNULL(customer_phone2, '')", 'is_bonuses': "is_bonus"}).values(
        'id', 'customer_name', 'customer_phone', 'driver_fee', 'customer_region__name',
        'driver_one_day_bonus', 'driver_two_day_bonus', 'status',
        'customer_district__name', 'customer_street', 'order_date_f', 'delivery_date_f', 'extra_phone').exclude(
        status=7).order_by("delivered_date"))


# maqsad haydovchilarga buyurtmalarni ko'rsatib ular o'zgartirishini ta'minlash
# tez ishlashi kerak
# ishlar rejasi
# orderlarni va mahsulotlarni olish kerak
# vue js pagination ishlatish kerak


def change_type_none(value):
    if value is not None:
        return value
    return ''


def make_json(o, products):
    return {"id": o.id,
            'status': o.status,
            'status_name': o.get_status_display(),
            'customer_name': o.customer_name,
            'customer_phone': o.customer_phone,
            'customer_phone2': change_type_none(o.customer_phone2),
            'customer_district': o.customer_district.name,
            'customer_street': o.customer_street,
            'total_price': o.order_products_total_price,
            'total_amount': o.order_products_total_ordered_amount,
            'updated_at': o.updated_at.strftime(("%Y-%m-%d")),
            'order_date': o.order_date.strftime(("%Y-%m-%d")),
            'delivery_date': o.delivered_date.strftime(("%Y-%m-%d")),
            'delivery_date_is_over': {True: 'true', False: 'false'}.get(o.is_delivered_date_over, 'false'),
            'driver_fee': change_type_none(o.driver_fee),
            'item_count': len(products),
            'bonus': o.bonus,
            'driver_is_bonus': {True: 'true', False: 'false'}.get(o.driver_is_bonus, 'false'),
            'products': products
            }


from django.core.paginator import Paginator


@login_required(login_url='/driver-login/')
@async_to_sync
async def driver_order_list(request):
    if request.user.is_active == False:
        return render(request, "driver_app/wait_active.html", {
            "message": "Sizning ma'lumotlaringiz hali tasdiqlanmadi. <br> Ma'lumotlar tasdiqlangach botni aktivlashtirish kodni sizga sms tarzda yoboramiz"})
    else:
        # if request.method == "POST":
        #     q = request.POST['query']
        #     order = Order.objects.filter(
        #         Q(customer_name__icontains=q) | Q(id__contains=q) | Q(customer_phone__contains=q) | Q(
        #             customer_phone2__contains=q), Q(status=3) | Q(status=4) | Q(status=5) | Q(status=6),
        #         driver_id=request.user.id).order_by("driver_shipping_start_date")
        #     return render(request, 'driver_app/order/order_list.html',
        #                   {'page_obj': order, 'count': order.count(), 'status': 0, 'query': q})

        order = Order.objects.filter(status=3, driver_id=request.user.id).order_by("driver_shipping_start_date")
        paginator = Paginator(order, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        return render(request, 'driver_app/order/order_list.html',
                      {'page_obj': page_obj, 'count': order.count(), 'status': 3, 'query': ""})


#
@login_required(login_url='/driver-login/')
@async_to_sync
async def driver_order_list_filter(request, status):
    if request.user.is_active == False:
        return render(request, "driver_app/wait_active.html", {
            "message": "Sizning ma'lumotlaringiz hali tasdiqlanmadi. <br> Ma'lumotlar tasdiqlangach botni aktivlashtirish kodni sizga sms tarzda yoboramiz"})
    else:
        order = Order.objects.filter(status=status, driver_id=request.user.id).order_by("driver_shipping_start_date")
        paginator = Paginator(order, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        return render(request, 'driver_app/order/order_list.html',
                      {'page_obj': page_obj, 'count': order.count(), 'status': status, 'query': ""})


@login_required(login_url='/driver-login/')
def autocomplete_order(request):
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
    if request.method == 'GET':
        q = request.GET.get('term', '').capitalize()
        status = request.GET.get('status', 4).capitalize()
        order = Order.objects.filter(
            Q(id__contains=q)|
            Q(customer_phone__contains=q) | Q(
                customer_phone2__contains=q),status=status, driver_id=request.user.id).order_by("driver_shipping_start_date")
        results = []
        for r in order[:15]:
            # results.append(
            #     {'id': r.id, 'name': r.customer_name, 'phone': r.customer_phone, 'phone2': r.customer_phone2})
            results.append(
                {
                    'id': r.id, 'customer_name': r.customer_name, 'customer_phone': r.customer_phone, 'customer_phone2': r.customer_phone2,
                    'customer_street': r.customer_street,'customer_district': r.customer_district.name,
                    'operator': get_not_none_operator_username(r.operator), 'status':r.status, 'status_name':r.get_status_display(),
                    'order_date':r.order_date.strftime(("%Y-%m-%d")), 'delivered_date':r.delivered_date.strftime(("%Y-%m-%d")),
                    'driver_fee':r.driver_fee, 'driver_is_bonus':{True :1, False:0}.get(r.driver_is_bonus), 'bonus':r.bonus,
                    'products':list(OrderProduct.objects.filter(order_id=r.id).values('product__name', 'ordered_amount', 'price')),
                    'order_products_total_ordered_amount':r.order_products_total_ordered_amount,
                    'order_products_total_price':r.order_products_total_price,'is_delivered_date_over':{True :1, False:0}.get(r.is_delivered_date_over),
                    'operator_note':get_not_none_value(r.operator_note),
                    "defective_product_order":get_not_none_value(r.defective_product_order_id),
                    "defective_product_order_products":get_not_none_value(r.defective_product_order_products)


                 })
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

import json

from django.http import JsonResponse


@login_required(login_url='/driver-login/')
def driver_change_order_status(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        order = Order.objects.filter(Q(status=3)|Q(status=6),id=body['order_id'], driver_id=request.user.id)

        # status 5 bekor qilinayotgan izoh kelishi kerak
        # status 6 qayta qungiroq vaqt kelishi kerak
        # status 4 hech narsa kerak emas
        if order:
            if body['next_status'] == 4:
                order_changed = Order.objects.get(id=body["order_id"])
                if order_changed.defective_product_order:
                    # order_changed.save()
                    return JsonResponse({'status': 404, 'messages': "Xozircha saqlolmaysiz"})

                else:
                    order.update(status=4, updated_at=datetime.now(), is_site_change=False)


                return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})
            # if body['next_status'] == 4:
            #     order.update(status=4, updated_at=datetime.now(), is_site_change=False)
            #     order_changed = Order.objects.get(id=body["order_id"])
            #     if order_changed.defective_product_order:
            #         order_changed.save()
            #     return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})
            # if body['next_status'] == 4:
                # try:
                #     with transaction.atomic():
                #         order_changed = order.first()
                #         if order_changed.defective_product_order:
                #             OrderProduct.objects.filter(order_id=order_changed.id).update(status=6, price=F('input_price'))
                #             sold_order = Order.objects.get(id=order_changed.defective_product_order.id)
                #             sold_order.driver_fee += order_changed.driver_fee
                #             sold_order.save()

                #             order_changed.status = '5'
                #             order_changed.updated_at=datetime.now()
                #             order_changed.is_site_change = False
                #             order_changed.save()
                #             return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

                #         else:
                #             order.update(status=4, updated_at=datetime.now(), is_site_change=False)
                #         return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})
                # except IntegrityError as e:
                    # e = "Xozircha tasdiqlash mumkun emas"
                    # return JsonResponse({'status': 404, 'messages': f"error :{e}"})
                
                # order_changed = order.first()
                # if order_changed.defective_product_order:
                #     OrderProduct.objects.filter(order_id=order_changed.id).update(status=6, price=F('input_price'))
                #     sold_order = Order.objects.get(id=order_changed.defective_product_order.id)
                #     sold_order.driver_fee += order_changed.driver_fee
                #     sold_order.save()

                    
                #     order_changed.status = '5'
                #     order_changed.updated_at=datetime.now()
                #     order_changed.is_site_change = False
                #     order_changed.save()
                #     return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

                # else:
                #     order.update(status=4, updated_at=datetime.now(), is_site_change=False)
                # return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

            if body['next_status'] == 5:
                order.update(status=5, driver_note=body['desc'], updated_at=datetime.now(), is_site_change=False)
                return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

            if body['next_status'] == 6:
                order.update(status=6, delivered_date=get_day(body['call_back_day']), updated_at=datetime.now(), is_site_change=False)
                return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

            return JsonResponse({'status': 404, 'messages': "Xato buyruq"})
        return JsonResponse({'status': 404, 'messages': "Bu buyurtma mavjud emas"})


def get_day(day):
    result = datetime.now() + timedelta(days=int(day))
    return result