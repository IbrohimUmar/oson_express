import datetime
import json

import requests
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import permission_classes
from django.db import transaction, IntegrityError

from config.connection.send_developer import send_private_message_developer
from order.models import Order, OrderProduct
from store.models import Product, ProductDeliveryPrice
from user.models import Regions, Districts, User
from django.http import JsonResponse

MyToken = "as2213dA2Dwwww21kwo12oasaaaaa123aaaaaaaaaadWALKSAMD.KA2KSMaslkdalsjdlkasdA123LDKMAaskdalskdasdas12dasdd213lasdlkasmldsadasdas"


import logging

developer_logger = logging.getLogger('developer_logger')


class MyTokenPermission(permissions.BasePermission):
    details = 'Siz hato buyruq berdingiz'
    def has_permission(self, request, view):
        if request.headers.get('MyToken') == str(MyToken):
            return True
        else:
            return False

from rest_framework.status import HTTP_400_BAD_REQUEST

HEADER = {'Content-type': 'application/json', 
"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
'Accept': 'application/json', 'MyToken': MyToken}




from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission

def get_or_create_operator(username):
    operator = User.objects.filter(username=username).first()
    if operator:
        return operator

    import random
    import string

    password_length = 10
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=password_length))
    print(password)

    operator=User.objects.create(
            username=username, first_name="Kiritilmagan", last_name="Kiritilmagan",password=make_password(password), password_text=password,
            special_fee_amount=1000, type=3, is_active=True, operator_id=None, is_staff=True
        )
    my_group = Group.objects.get(name='operatorlar')
    my_group.user_set.add(operator)
    return operator



@permission_classes([MyTokenPermission])
class CreateOrderFromOtherSite(APIView):
    def post(self, request):
        if Order.objects.filter(site_order_id=request.data['order_id'], site=request.data['site_id']).exists():
            return Response({"messages": "Bu id li buyurtma kiritilgan"}, status=400)
        r = request.data
        try:
            with transaction.atomic():
                district = Districts.objects.filter(region_id=r['region'], id=r['district']).first()
                if not district:
                    developer_logger.error(str(f"createOrderFromOtherSitesError district error {r}"), exc_info=True)
                    raise IntegrityError
                
                #district = Districts.objects.get(id=r['district'])
                
                
                if r.get("operator_id", None):
                    operator = User.objects.get(id=r['operator_id'])
                else:
                    operator = get_or_create_operator(r['operator_username'])
                order = Order.objects.create(operator=operator, site=r['site_id'],
                                             site_order_id=r['order_id'],
                                             customer_name=r['customer_name'][:50],
                                             customer_phone=r['customer_phone'][:30],
                                             customer_phone2=r['customer_phone2'][:30],
                                             customer_region_id=r['region'],
                                             seller_fee=r['seller_fee'],
                                             customer_district_id=r['district'],
                                             customer_street=r['street'],
                                             order_date=datetime.datetime.today().strftime(("%Y-%m-%d")),
                                             delivered_date=r['delivered_date'],
                                             status=1,
                                             driver_is_bonus=district.driver_is_bonus,
                                             driver_one_day_bonus=district.driver_one_day_bonus,
                                             driver_two_day_bonus=district.driver_two_day_bonus,
                                             )
                items = []
                for index, p in enumerate(r['products']):
                    items.append(
                        OrderProduct(status=1, order_id=order.id,
                                     product_id=p['id'],
                                     product_item=self.get_product_item(p['id'], p['name']),
                                     ordered_amount=p['amount'],
                                     price=p.get('total_price', p["price"]),

                                     product_color=self.get_product_color(p.get('selected_color', None)),
                                     product_size=self.get_product_size(p.get('selected_size', None)),

                                     color=p.get('selected_color', ""),
                                     size=p.get('selected_size', ""),
                                     input_price=Product.objects.get(id=p['id']).price
                                     )
                    )
                OrderProduct.objects.bulk_create(items)
                order.update_driver_fee()
        except IntegrityError as e:
            developer_logger.error(str(f"createOrderFromOtherSitesError {str(e)}"), exc_info=True)
            return Response({"messages": "Bu buyurtma ma'lumotlar saqlashda muammo"}, status=500)
        return Response({"messages":"o'zgartirildi"}, status=200)


    def get_product_item(self, product_id, name):
        item = ProductItems.objects.filter(name=name, product_id=product_id)
        if item:
            return item.first()
        return ProductItems.objects.filter(product_id=product_id).first()


    def get_product_size(self, obj):
        if obj:
            if len(str(obj)) > 3:
                from store.models import ProductSize
                size = ProductSize.objects.filter(id=obj['id']).first()
                return size
        return None

    def get_product_color(self, obj):
        if obj:
            print(obj)
            if len(str(obj)) > 3:
                from store.models import Colors
                color = Colors.objects.filter(name=obj['name']).first()
                return color
        return None

import datetime
from datetime import timedelta
import threading

def update_order_status_on_other_sites(site_id, url):
    # send_private_message_developer('cron ishladi')

    def json_data(site, url):
        order = Order.objects.filter(site=site, site_order_id__isnull=False, is_site_change=False)

        if order.filter(Q(status=3) | Q(status=4) | Q(status=5) | Q(status=0)).exists():
            before_24_hours = datetime.datetime.now() - timedelta(hours=24)
            #before_48_hours = datetime.datetime.now() - timedelta(hours=48)
            # before_72_hours = datetime.datetime.now() - timedelta(hours=72)

            data = {
                'archived': list(order.filter(status=0).values_list('site_order_id', flat=True)),
                'being_delivered': list(order.filter(status=3).values_list('site_order_id', flat=True)),
                'canceled': list(order.filter(status=5, updated_at__lte=before_24_hours).values_list('site_order_id', flat=True)),
                # 'delivered': list(order.filter(status=4, payment_status='3').values_list('site_order_id', flat=True)),
                'delivered': list(order.filter(status=4).values_list('site_order_id', flat=True)),

            }
            status = try_to_send(url, data)
            if status == 200:
                return order.filter(Q(status=3) | Q(status=4) | Q(status=5, updated_at__lte=before_24_hours) | Q(status=0)).update(is_site_change=True)
                
            developer_logger.error(str(f"order status avto change error {str(status)}"), exc_info=True)

    def try_to_send(url, data):
        for a in range(5):
            try:
                response = requests.post(url,
                                         data=json.dumps(data), headers=HEADER, timeout=50)
                return response.status_code
            except requests.exceptions.RequestException as err:
                send_private_message_developer(f"Elituvchi avto status o'zgartiradigan funcda error sayt : {url}")
                developer_logger.error(str(f"order status avto change error {str(err)}"), exc_info=True)
                return 400
    json_data(site_id, url)



# https://elituvchi.savdo24.com/update_order_stataus_on_other_sites/alskdlasm5diowqdmsamxlakm1claksdoakspdkas21lcklxmklncks/1
def check_order(request, code, site_id):
    if code == "alskdlasm5diowqdmsamxlakm1claksdoakspdkas21lcklxmklncks":
        if int(site_id) == 1:
            update_order_status_on_other_sites(1, "https://mahsulot.com/api/order-change-satus-from-elituvchi/" )
            # thread = threading.Thread(target=update_order_status_on_other_sites, args=(1, "https://mahsulot.com/api/order-change-satus-from-elituvchi/", ))
            # thread.start()
        elif int(site_id) == 2:
            thread = threading.Thread(target=update_order_status_on_other_sites, args=(2, "https://airshop.uz/api/order-change-satus-from-elituvchi/", ))
            thread.start()
        elif int(site_id) == 6:
            thread = threading.Thread(target=update_order_status_on_other_sites, args=(6, "https://premiumshop.uz/api/order-change-satus-from-elituvchi/", ))
            thread.start()
        elif int(site_id) == 7:
            thread = threading.Thread(target=update_order_status_on_other_sites, args=(7, "https://my-bazar.com/api/order-change-satus-from-elituvchi/", ))
            thread.start()

        elif int(site_id) == 3:
            thread = threading.Thread(target=update_order_status_on_other_sites, args=(3, "https://savdo24.com/api/order-change-satus-from-elituvchi/", ))
            thread.start()
        return JsonResponse({"status":'200'})
    return JsonResponse({"error":'500'})
















# https://elituvchi.savdo24.com/update_changed_order_stataus_on_other_sites/alskdlasm5diowqdmsamxlakm1claksdoakspdkas21lcklxmklncksa
def check_changed_order(request, code):
    if code == "alskdlasm5diowqdmsamxlakm1claksdoakspdkas21lcklxmklncksa":
        def json_data(site, url):
            order = Order.objects.filter(site=site, site_order_id__isnull=False, is_site_change=True)
            if order.filter(Q(status=3) | Q(status=4) | Q(status=5)| Q(status=0)).exists():
                before_24_hours = datetime.datetime.now() - timedelta(hours=24)
                #before_48_hours = datetime.datetime.now() - timedelta(hours=48)
                #before_48_hours = datetime.datetime.now() - timedelta(hours=24)
                data = {
                    # 'archived': list(order.filter(status=0).values_list('site_order_id', flat=True)),
                    # 'being_delivered': list(order.filter(status=3).values_list('site_order_id', flat=True)),
                    
                    
                    'canceled': list(order.filter(status=5, updated_at__lte=before_24_hours).values_list('site_order_id', flat=True)),
                    # 'delivered': list(order.filter(status=4, updated_at__gte=before_24_hours).values_list('site_order_id', flat=True)),
                    
                
                      'archived':[],
                      'being_delivered':[],

                    # 'canceled':[],
                    'delivered':[],
                }
                status = try_to_send(url, data)
                if status == 200:
                    send_private_message_developer(str(url) + ' :check changed order count'+ str(order.count()))
                return {"site":site, "Buyurtma_soni":order.count()}
        def try_to_send(url, data):
            for attempt in range(1, 6):  # 5 deneme yapılacak
                try:
                    response = requests.post(url, data=json.dumps(data), headers=HEADER, timeout=50)
                    response.raise_for_status()  # Hata durumunda istisna fırlatır
                    return response.status_code
                except requests.exceptions.RequestException as err:
                    send_private_message_developer(f"Elituvchi all order avto status o'zgartiradigan funcda error sayt : {url}")
                    developer_logger.error(f"order all status avto change error: {err}", exc_info=True)
                    if attempt == 5:
                        return 400
                
            #     response = requests.post(url, data=json.dumps(data), headers=HEADER)
            #     if int(response.status_code) == 200:
            #         return 200
            # send_private_message_developer(str(url)+' :saytga ulanib bumadi')
            # return 400

        response1=json_data(1, "https://mahsulot.com/api/all-order-change-satus-from-elituvchi/")
        # response2=json_data(2, "https://airshop.uz/api/all-order-change-satus-from-elituvchi/")
        # response3=json_data(3, "https://savdo24.com/api/order-change-satus-from-elituvchi/")
        # response4=json_data(6, "https://premiumshop.uz/api/all-order-change-satus-from-elituvchi/")
        # response5=json_data(7, "https://my-bazar.com/api/all-order-change-satus-from-elituvchi/")
        # return JsonResponse({"status":'200', 'response':[response1, response2, response3, response4, response5]})

        return JsonResponse({"status":'200', 'response':[response1]})
    return JsonResponse({"sta":'sas'})



from threading import Thread
from requests import post, exceptions

from django.core.paginator import Paginator


# def update_order_status_on_other_sitesss(site, url):
#     order = Order.objects.filter(site=site, site_order_id__isnull=False, is_site_change=True)
#     if order.filter(status__in=[3, 4, 5, 0]).exists():
#         archived_orders = order.filter(status=0)
#         if archived_orders.count() > 0:
#             # Her gün için 5000 sipariş gönder
#                 paginator = Paginator(archived_orders, 10000)
#                 for page in paginator.page_range:
#                     group = paginator.page(page).object_list
#                     data = {
#                         'archived': list(group.values_list('site_order_id', flat=True)),
#                         "being_delivered":[],
#                         "canceled":[],
#                         "delivered":[],
#                     }
#                     status = try_to_send(url, data)
#                     if status != 200:
#                         return {"site": site, "Buyurtma_soni": order.count(), "error": "Siteye gönderim başarısız"}
#                     developer_logger.info(str(f"arxivlandilar o'zgartirildi "), exc_info=True)

                    
#         being_delivered = order.filter(status=3)
#         if being_delivered.count() > 0:
#             # Her gün için 5000 sipariş gönder
#                 paginator = Paginator(being_delivered, 10000)
#                 for page in paginator.page_range:
#                     group = paginator.page(page).object_list
#                     data = {
#                         'archived': [],
#                         "being_delivered":list(group.values_list('site_order_id', flat=True)),
#                         "canceled":[],
#                         "delivered":[],
#                     }
#                     status = try_to_send(url, data)
#                     if status != 200:
#                         return {"site": site, "Buyurtma_soni": order.count(), "error": "Siteye gönderim başarısız"}
#                     developer_logger.info(str(f"yetkazilmoqlar url : {url} o'zgartirildi "), exc_info=True)


#         canceled = order.filter(status=5, updated_at__lte=datetime.datetime.now() - timedelta(hours=24))
#         if canceled.count() > 0:
#                 paginator = Paginator(canceled, 10000)
#                 for page in paginator.page_range:
#                     group = paginator.page(page).object_list
#                     data = {
#                         'archived': [],
#                         "being_delivered":[],
#                         "canceled":list(group.values_list('site_order_id', flat=True)),
#                         "delivered":[],
#                     }
#                     status = try_to_send(url, data)
#                     if status != 200:
#                         return {"site": site, "Buyurtma_soni": order.count(), "error": "Siteye gönderim başarısız"}
#                     developer_logger.info(str(f"Bekor qilindilar url : {url}, soni : {canceled.count()} o'zgartirildi "), exc_info=True)

#         delivered = order.filter(status=4)
#         if delivered.count() > 0:
#                 paginator = Paginator(delivered, 10000)
#                 for page in paginator.page_range:
#                     group = paginator.page(page).object_list
#                     data = {
#                         'archived': [],
#                         "being_delivered":[],
#                         "canceled":[],
#                         "delivered":list(group.values_list('site_order_id', flat=True)),
#                     }
#                     status = try_to_send(url, data)
#                     if status != 200:
#                         return {"site": site, "Buyurtma_soni": order.count(), "error": "Siteye gönderim başarısız"}
#                     developer_logger.info(str(f"sotildilar o'zgardi url : {url}, soni : {delivered.count()} o'zgartirildi "), exc_info=True)
                        
#         return {"site": site, "Buyurtma_soni": order.count()}

# def update_order_status_on_other_sites(site, url):
#     order = Order.objects.filter(site=site, site_order_id__isnull=False, is_site_change=True)
#     if order.filter(Q(status__in=[3, 4, 5, 0]) | Q(status=5, updated_at__lte=datetime.datetime.now() - timedelta(hours=24))).exists():
#         paginator = Paginator(order, 10000)
#         all_results = []
#         for page in paginator.page_range:
#             group = paginator.page(page).object_list
#             data = {
#                 'archived': list(group.filter(status=0).values_list('site_order_id', flat=True)),
#                 'being_delivered': list(group.filter(status=3).values_list('site_order_id', flat=True)),
#                 'canceled': list(group.filter(status=5).values_list('site_order_id', flat=True)),
#                 'delivered': list(group.filter(status=4).values_list('site_order_id', flat=True)),
#             }
#             status = try_to_send(url, data)
#             if status != 200:
#                 return {"site": site, "Buyurtma_soni": order.count(), "error": "Siteye gönderim başarısız"}
#         if 200 in all_results:
#             send_private_message_developer(str(url) + ' :check changed order count' + str(order.count()))
#         return {"site": site, "Buyurtma_soni": order.count()}


# def update_order_status_on_other_sites(site, url):
#     order = Order.objects.filter(site=site, site_order_id__isnull=False, is_site_change=True)
#     if order.filter(Q(status=3) | Q(status=4) | Q(status=5) | Q(status=0)).exists():
#         before_24_hours = datetime.datetime.now() - timedelta(hours=24)
#         order_groups = [order[i:i + 10000] for i in range(0, len(order), 10000)]
#         all_results = []
#         for group in order_groups:
#             data = {
#                 'archived': list(group.filter(status=0).values_list('site_order_id', flat=True)),
#                 'being_delivered': list(group.filter(status=3).values_list('site_order_id', flat=True)),
#                 'canceled': list(
#                     group.filter(status=5, updated_at__lte=before_24_hours).values_list('site_order_id', flat=True)),
#                 'delivered': list(
#                     group.filter(status=4, updated_at__lte=before_24_hours).values_list('site_order_id', flat=True)),

#             }
#             status = try_to_send(url, data)
#             all_results.append(status)
#         if 200 in all_results:
#             send_private_message_developer(str(url) + ' :check changed order count' + str(order.count()))
#         return {"site": site, "Buyurtma_soni": order.count()}


# def try_to_send(url, data):
#     for a in range(5):
#         try:
#             response = post(url, data=json.dumps(data), headers=HEADER)
#             if response.status_code == 200:
#                 send_private_message_developer(f" {data} - yuborildi")
#                 return 200
#         except TimeoutError:
#             send_private_message_developer(f"{url}: Timeout hatası")
#             continue
#         except ConnectionError:
#             send_private_message_developer(f"{url}: Bağlantı hatası")
#             continue
#         except exceptions.HTTPError as e:
#             send_private_message_developer(f"{url}: HTTP hatası ({e.status_code})")
#     return 400



# def check_changed_order(request, code):
#     if code != "alskdlasm5diowqdmsamxlakm1claksdoakspdkas21lcklxmklncks":
#         return JsonResponse({"token":'error'})
#     sites = [(1, "https://mahsulot.com/api/all-order-change-satus-from-elituvchi/"),
#              (2, "https://airshop.uz/api/all-order-change-satus-from-elituvchi/"),
#              (3, "https://savdo24.com/api/order-change-satus-from-elituvchi/"),
#              (6, "https://premiumshop.uz/api/all-order-change-satus-from-elituvchi/"),
#              (7, "https://my-bazar.com/api/all-order-change-satus-from-elituvchi/")]

#     threads = []
#     results = []
#     for site_id, url in sites:
#         thread = Thread(target=update_order_status_on_other_sites, args=(site_id, url))
#         threads.append(thread)
#         thread.start()
#     # for thread in threads:
#     #     thread.join()
#     #     results.append(thread.return_value)
#     return JsonResponse({"status": '200', 'response': []})
