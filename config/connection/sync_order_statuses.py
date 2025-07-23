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
from rest_framework.status import HTTP_400_BAD_REQUEST

import datetime
from datetime import timedelta
import threading
import logging

developer_logger = logging.getLogger('developer_logger')
MyToken = "as2213dA2Dwwww21kwo12oasaaaaa123aaaaaaaaaadWALKSAMD.KA2KSMaslkdalsjdlkasdA123LDKMAaskdalskdasdas12dasdd213lasdlkasmldsadasdas"

# HEADER = {'Content-type': 'application/json',
HEADER = {'Content-type': 'application/json', 
"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
'Accept': 'application/json', 'MyToken': MyToken}



class MyTokenPermission(permissions.BasePermission):
    details = 'Siz hato buyruq berdingiz'
    def has_permission(self, request, view):
        if request.headers.get('MyToken') == str(MyToken):
            return True
        else:
            return False



def sync_cahnged_order_statuses(request, site_id):
    pass

status_name = {
                    1:"accepted",
                    2:"accepted",
                    7:"accepted",
                    8:"accepted",
                    
                    0:"archived",
                    3:"being_delivered",
                    4:"delivered",
                    5:"canceled",
                        }

# https://elituvchi.savdo24.com/sync_all_order_statuses/alskdlasm5diowqdmsamxlakm1claksdoakspdkas21lcklxmklncksa
def sync_all_order_statuses(request, code):
    if code != "alskdlasm5diowqdmsamxlakm1claksdoakspdkas21lcklxmklncksa":
        return JsonResponse({"error": "siz kerakli parametrlarni kiritmadingiz"})
    sites = [
        # {"site_id": 1, "url": "https://operator.mahsulot.com/api/all-order-change-satus-from-elituvchi/"},

        # {"site_id": 1, "url": "https://mahsulot.com/api/all-order-change-satus-from-elituvchi/"},
        # {"site_id": 2, "url": "https://airshop.uz/api/all-order-change-satus-from-elituvchi/"},
        # {"site_id": 3, "url": "https://savdo24.com/api/all-order-change-satus-from-elituvchi/"},
        {"site_id": 6, "url": "https://premiumshop.uz/api/all-order-change-satus-from-elituvchi/"},

    ]

    def run_site_sync_chain(sites_list):
        for site in sites_list:
            sync_obj = AllOrderStatusSync(site['site_id'], site['url'])
            sync_obj.process_orders()
            send_private_message_developer(f"all order sync function successfully updated : {site['url']}")

    # run_site_sync_chain(sites)
    thread = threading.Thread(target=run_site_sync_chain, args=[sites])
    thread.start()
    return JsonResponse({"status": '200', "message": "Jarayon boshlandi"})

#  0, 3, 4, 5      -  1, 2    0, 3, 4, 5

class AllOrderStatusSync:
    def __init__(self, site, url, allowed_status_list=[0, 3, 5, 4], batch_size=10000):
        self.site = site
        self.url = url
        self.allowed_status_list = allowed_status_list
        self.batch_size = batch_size

    def process_orders_batches(self, url, data):
        for attempt in range(1, 6):  # 5 deneme yapılacak
            try:
                developer_logger.error(f"order all status avto change error: {data}", exc_info=True)
                response = requests.post(url, data=json.dumps(data), headers=HEADER, timeout=50)
                response.raise_for_status()  # Hata durumunda istisna fırlatır
                return response.status_code
            except requests.exceptions.RequestException as err:
                send_private_message_developer \
                    (f"Elituvchi all order avto status o'zgartiradigan funcda error sayt : {url}")
                developer_logger.error(f"order all status avto change error: {err}", exc_info=True)
                if attempt == 5:
                    return 400

    def process_orders(self):
        developer_logger.info("Uzgartirish boshlandi")

        order_query = Order.objects.filter(
            site=self.site,
            site_order_id__isnull=False,
            is_site_change=True,
            status__in=self.allowed_status_list,
        )

        if not order_query.exists():
            developer_logger.info(f"Status o'zgartiriladigan buyurtma mavjud emas")
            return False

        if order_query.exists():
                statuses = self.allowed_status_list
                for status in statuses:
                    order_ids = list(order_query.filter(status=status)
                                     .values_list('site_order_id', flat=True))
                    if order_ids:
                        for i in range(0, len(order_ids), self.batch_size):
                            send_data = {"accepted":[],"archived": [], "being_delivered": [],
                                         "delivered": [], "canceled": [],}
                            send_data[status_name.get(status)] = order_ids[i:i + self.batch_size]
                            self.process_orders_batches(self.url, send_data)

