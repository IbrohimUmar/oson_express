from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from user.models import User, Districts
from order.models import Order
from store.models import Product
from django.contrib.auth.decorators import permission_required
from django.contrib import messages

from django.http import JsonResponse
import datetime
from order.models import OrderProduct
from cash.models import Cash
from user.models import CashierUser, User
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

from config.cash.crud import cashier_balance_update

import logging

developer_logger = logging.getLogger('developer_logger')
import threading
from django.db.models import Q, F
import json
from store.models import Product, ProductVariable
from django.db.models import F, Q
from django.db import transaction, IntegrityError

import random
from barcode import EAN13
from order.models import Order

from order.models import Order, OrderProduct
from django.db import transaction, IntegrityError
from datetime import datetime

# xojiakbar xamiodv       orders = Order.objects.filter(status="1", is_print=True, customer_region_id=11, customer_district_id__in=[150, 159, 160, 161, 162, 166, 212, 241, 242])
# abdul fatttoh 155, 157, 158, 164, 167, 213, 215, 239


#     orders = Order.objects.filter(status="1", is_print=True, customer_region_id=14, customer_district_id__in=[200, 203, 208, 218])

# def development(request):
#     # or_list = [1, 2, 3, 4]
#     # orders = Order.objects.filter(site=1, site_order_id__in=or_list).count()

#     orders = Order.objects.filter(site=1, site_order_id__in=or_list).values_list('site_order_id', flat=True)

#     # Orders listesinde olmayan site_order_id değerlerini bul
#     not_in_orders = [element for element in or_list if element not in orders]


#     return JsonResponse({"list_len":not_in_orders}, safe=False)


# #     orders = Order.objects.filter(status="1", is_print=True, customer_region_id=14, customer_district_id=218)
#     orders = Order.objects.filter(status="1", customer_region_id=14, id__in=[693837, 698803])

#     # orders = Order.objects.filter(status="3", is_print=True).values("customer_region", 'customer_district')
#     driver_id = 2919
#     response = "not"
#     if orders:
#         response = printed_order_send_product(orders, driver_id)

#     or_pro = OrderProduct.objects.filter(order__is_print=True, order__status="3", ordered_amount=0)

#     or_pro = OrderProduct.objects.filter(order__is_print=True, ordered_amount=0)
#     for o in or_pro:
#         out_item = OutputProductItems.objects.filter(order_product=o)
#         if out_item:
#             amount = out_item.first().amount
#             o.status="4"
#             o.ordered_amount = amount
#             o.amount = amount
#             o.save()
#     aor_pro = OrderProduct.objects.filter(order__is_print=True, ordered_amount=0).values("order__id", 'order__status', 'driver_id')


import datetime
from django.db.models import Q, ExpressionWrapper
from django.db import models
from django.db.models import Sum, F, Q, Count
from store.models import ProductCollectionItem

from warehouse.models import WarehouseOperationAndOrderRelations
from warehouse.models import WareHouseStock

from config.warehouse.services.warehouse_operation_item_manager import WarehouseOperationItemManager
from config.warehouse.services.warehouse_operation_item_details_manager import WarehouseOperationItemDetailsManager
from order.models import Order

from warehouse.models import WarehouseOperation, WareHouse, WarehouseOperationItem, WarehouseOperationItemDetails, \
    WarehouseOperationAndOrderRelations
from config.warehouse.services.warehouse_operation_manager import WarehouseOperationManager


class InsufficientStockError(Exception):
    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"{product_name} shu mahsulotdan omborda yetarli emas.")


def driver_return_product_from_driver(driver, order, responsible):
    # order.status = 5
    # order.cancelled_status = 3
    # order.is_site_change = False
    # # order.updated_at = datetime.datetime.now()
    # order.save()
    Order.objects.filter(id=order.id).update(status=5, cancelled_status=3, is_site_change=False)
    # ------operation get or create qilamiz
    to_warehouse = WareHouse.objects.get(id=5)
    warehouse_operation_service = WarehouseOperationManager()
    warehouse_operation_item_details_services = WarehouseOperationItemDetailsManager()
    warehouse_operation_item_services = WarehouseOperationItemManager()
    warehouse_operation = warehouse_operation_service.warehouse_operation_driver_return_product_get_or_create(
        to_warehouse, driver, responsible)
    WarehouseOperationAndOrderRelations.objects.create(action=2, warehouse_operation=warehouse_operation,
                                                       order=order)

    order_products = OrderProduct.objects.filter(type__in=[1, 3], status__in=[4, 6], order=order)
    # buni aylanib harbir temni detailslariga mos boshqalarini yaratish kerak
    for order_product in order_products:
        amount = order_product.ordered_amount
        if order_product.type == '3':
            amount = order_product.main_order_product.ordered_amount
        product = order_product.product
        product_variable = order_product.product_variable
        warehouse_operation_item = warehouse_operation_item_services.operation_item_create(warehouse_operation,
                                                                                           product,
                                                                                           product_variable,
                                                                                           None, amount)
        leave_checked_amount = amount
        warehouse_operation_item_details = WarehouseOperationItemDetails.objects.filter(order_product=order_product,
                                                                                        leave_amount__gt=0)
        for warehouse_operation_item_detail in warehouse_operation_item_details:
            warehouse_operation_item_details_services.operation_item_details_create_return_product(
                warehouse_operation_item_detail,
                warehouse_operation,
                warehouse_operation_item)
            leave_checked_amount -= warehouse_operation_item_detail.leave_amount
            warehouse_operation_item_detail.leave_amount = 0
            warehouse_operation_item_detail.save()

        if leave_checked_amount != 0:
            raise InsufficientStockError
        order_product.amount = 0
        if order_product.status == '4':
            order_product.status = "5"
        elif order_product.status == "6":
            order_product.status = "7"
        order_product.save()

    OrderProduct.objects.filter(type=2, status__in=[4, 6], order=order).update(amount=0, status="5")
    OrderProduct.objects.filter(type=2, status=7, order=order).update(amount=0, status="6")
    return True


# def development(request):
#     superuser = User.objects.get(id=1)

#     try:
#         with transaction.atomic():
#             cancelled_orders = Order.objects.filter(driver_id=64, status=5, cancelled_status="1", output_product__isnull=True).select_for_update()

#             # cancelled_orders = Order.objects.filter(driver_id=2919, status=5, cancelled_status="1", output_product__isnull=True).select_for_update()
#             count_order = cancelled_orders.count()
#             for i in cancelled_orders[:100]:
#                 driver = i.driver
#                 driver_return_product_from_driver(driver, i, superuser)
#                 # Order.objects.filter(id=i.id).update(status=5, cancelled_status=3, is_site_change=False)


#                 # OrderProduct.objects.filter(status=4, order=i).update(amount=0, status="5")

#                 # OrderProduct.objects.filter(type=2, status__in=[4, 6], order=i).update(amount=0, status="5")
#                 # OrderProduct.objects.filter(type=2, status=7, order=i).update(amount=0, status="6")

#             # result = 2
#             return JsonResponse({'count': count_order}, safe=False)

#             # orders = Order.objects.filter(driver__isnull=False, cancelled_status='1', status=5, output_product__isnull=False)
#             # for i in orders:
#             #     OrderProduct.objects.filter(order=i, status=4).update(
#             #         status=5, amount=0
#             #     )
#             #     OrderProduct.objects.filter(order=i, status=6).update(
#             #         status=7, amount=0
#             #     )
#             #     i.cancelled_status=3
#             #     i.save()
#             # ordered_pro1 = OrderProduct.objects.filter(order__status=5, order__cancelled_status="3", status=4, order__output_product__isnull=False).update(status=5)
#             # ordered_pro2 = OrderProduct.objects.filter(order__status=5, order__cancelled_status="3", status=6, order__output_product__isnull=False).update(status=7)


#             # ordered_pro = OrderProduct.objects.filter(order__status=5, order__cancelled_status="3", status=4, order__output_product__isnull=False).values("id", 'updated_at', 'order__cancelled_status', 'order__status')
#             # cancelled_orders = Order.objects.filter(driver__isnull=False, status=5, cancelled_status="1", output_product__isnull=False)
#             # return JsonResponse({'len':len(cancelled_orders),'count': list(cancelled_orders.values("updated_at", 'id')), 'or_pro_count':len(ordered_pro), 'or_pro':list(ordered_pro)}, safe=False)
#     except IntegrityError as e:
#         developer_logger.error(str(f"config.driver.send_products integration error : {str(e)}"), exc_info=True)
#         return JsonResponse({ 'error':e}, safe=False)


# def development(request):

#     three_days_ago = datetime.datetime.today() - datetime.timedelta(days=2)
#     orders = Order.objects.filter(status=1, created_at__lte=three_days_ago, defective_product_order__isnull=True, operator_order_id__isnull=False)

#     data = []
#     try:
#         with transaction.atomic():
#             for o in orders:
#                         # data.append({"order_id":o.id, 'site_id':o.site_order_id, 'operator_order_id':o.operator_order_id, 'operator_id':o.operator.id})

#                         operator_order = OperatorOrder.objects.get(id=o.operator_order_id)
#                         operator_order.operator = None
#                         operator_order.status = 1
#                         operator_order.is_change = True
#                         operator_order.save()

#                         o.operator_order_id = None
#                         o.site_order_id = None
#                         o.status = 0
#                         o.delete_desc = "Buyurtma eskirib qolgani sababli 2"
#                         o.save()
#                         # return JsonResponse({"count":orders.count()}, safe=False)

#     except IntegrityError as e:
#             # developer_logger.error(str(f"config.driver.send_products integration error : {str(e)}"), exc_info=True)
#         return JsonResponse({ 'error':e}, safe=False)


#     return JsonResponse({"count":len(data), 'data':data}, safe=False)


def development(request):
    from config.barcode import barcode_generate
    # cash = Cash.objects.filter(type='1', from_user__type='2').update(leave_amount=F("amount"))
    equals_order = []
    # print(i)
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()

    # driver = 127
    # warehouse_operation = WarehouseOperation.objects.get(id=1189, action="3")
    # warehouse_relations_id = list(
    #     WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation=warehouse_operation).values_list(
    #         "order_id", flat=True))
    # Order.objects.filter(id__in=warehouse_relations_id).update(driver_id=driver)
    # OrderProduct.objects.filter(order_id__in=warehouse_relations_id).update(driver_id=driver)
    #
    # warehouse_operation.to_warehouse_responsible_id = driver
    # warehouse_operation.save()
    # for o in Order.objects.filter(id__in=warehouse_relations_id):
    #     o.update_driver_fee()

    User.objects.filter(type='3').update(is_active=False)

    # 2 gün öncesi
    # two_days_ago = now - timedelta(days=2)
    #
    # from operators.models.order_models import OperatorOrder
    # op_order = OperatorOrder.objects.filter(status='8',operator__username__in=[998958801333,998886177666,998883427337], created_at__gte=two_days_ago)
    # # for i in op_order:
    # #     print(i.operator.username, i.created_at)
    # print(op_order.count())
    # from config.cash.crud import check_paid_orders
    # drivers = User.objects.filter(type='2', is_active=True)
    # for d in drivers:
    #     check_paid_orders(d.id)
    #     print('tayyor :', d.id)
    # Order.objects.filter(id=i['id'], driver_id=56).update(status=i['status'], updated_at=i['updated_at'], is_site_change=False)

    # op = Order.objects.filter(id__in=orders).values("id", 'status', 'updated_at', 'defective_product_order')

    # b = Order.objects.filter(status__in=[1, 7, 8], barcode__isnull=True)
    # for i in b:
    #     i.barcode = barcode_generate()
    #     i.save()
    # operation_id = 1635
    # from_driver_id = 3944
    # to_driver_id = 976

    # warehouse_operation = WarehouseOperation.objects.filter(id=operation_id, to_warehouse_responsible_id=from_driver_id).update(to_warehouse_responsible_id=to_driver_id)
    # warehouse_relations_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=operation_id).values_list("order_id", flat=True))
    # Order.objects.filter(id__in=warehouse_relations_id).update(driver_id=to_driver_id)
    # OrderProduct.objects.filter(order_id__in=warehouse_relations_id).update(driver_id=to_driver_id)
    return JsonResponse({"count": len(equals_order), 'order': equals_order}, safe=False)


def development_old(request):
    # orders = Order.objects.filter(status__in=[1, 2, 3, 7, 8], defective_product_order__isnull=False, driver_fee=0).update(driver_fee=10000)

    # order = Order.objects.filter(id=791661).update(site_order_id=None)
    # order = Order.objects.filter(status=1).update(driver=None)
    # order = Order.objects.filter(status__in=[7, 8]).count()
    # if order == 0:
    # WareHouseStock.objects.filter(warehouse_id=1).update(attachment_amount=F("amount"))

    # warehouse_operation = WarehouseOperation.objects.filter(id=1234, to_warehouse_responsible_id=64).update(to_warehouse_responsible_id=2917)
    # warehouse_relations_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=1234).values_list("order_id", flat=True))
    # Order.objects.filter(id__in=warehouse_relations_id).update(driver_id=2917)
    # OrderProduct.objects.filter(order_id__in=warehouse_relations_id).update(driver_id=2917)

    # checked_count = 0
    # checked_pro_name = []
    break_name = []

    from config.barcode import barcode_generate

    b = Order.objects.filter(status__in=[1, 7, 8], barcode__isnull=True)
    for i in b:
        i.barcode = barcode_generate()
        i.save()

    # try:
    #     with transaction.atomic():
    #         ch = []
    #         for o in order:
    #             order_products = OrderProduct.objects.filter(order=o, product_id__in=cancelled_pro_id)
    #             if not order_products:

    #                 order_product = OrderProduct.objects.filter(order=o)
    #                 # ch.append(order_product.values('product__name'))

    #                 if order_product.count() == 1:

    #                     or_pro = order_product.first()
    #                     if or_pro.product.is_collection == False and or_pro.product_variable is None:
    #                         variable = ProductVariable.objects.filter(product=or_pro.product, is_active=True).first()
    #                         if variable:
    #                             ch.append(o.id)
    #                             or_pro.product_variable=variable
    #                             or_pro.type="1"
    #                             or_pro.save()
    #         return JsonResponse({"count": ch}, safe=False)

    # except IntegrityError as e:
    #     return JsonResponse({"count": e}, safe=False)
    # items = []
    # break_count = 0
    # try:
    #     with transaction.atomic():
    #         for o in order:
    #             order_products = OrderProduct.objects.filter(order=o, product_id__in=cancelled_pro_id)
    #             if order_products:
    #                 break_count += 1
    #                 # break
    #             if not order_products:

    #                 order_product = OrderProduct.objects.filter(order=o)
    #                 if ord:
    #                     item = order_product.first()
    #                     if item.product.is_collection == True:
    #                         collections = ProductCollectionItem.objects.filter(product=item.product).first()
    #                         # col = [{"pro_name":i.name, 'variable_count':ProductVariable.objects.filter(product=i, is_active=True).count()} for i in collections.collection.all()]
    #                         items.append(
    #                             f"order_id {item.order.id}, name : {item.product.name}, is_collection : {item.product.is_collection}, order_pro_type : {item.type}, variable : {col}")

    # for i in collections.collection.all():

    #     variable = ProductVariable.objects.filter(product=i, is_active=True).first()
    #     OrderProduct.objects.get_or_create(main_order_product=item, type="3", product=i, product_variable=variable)

    # item.type="2"
    # item.save()

    # # col = [{"pro_name":i.name, 'variable_count':ProductVariable.objects.filter(product=i, is_active=True).count()} for i in collections.collection]
    # items.append(
    #     f"order_id {item.order.id}, name : {item.product.name}, is_collection : {item.product.is_collection}, order_pro_type : {item.type}")

    # for item in OrderProduct.objects.filter(order=o):
    #     items.append(f"order_id {item.order.id}, name : {item.product.name}, is_collection : {item.product.is_collection}, order_pro_type : {item.type}, variable : {item.product_variable}")

    # except IntegrityError as e:
    #     return JsonResponse({"count": e}, safe=False)

    # ac_count += 1
    # product = item.product
    # accepted_pro_id.append(f"id : {product.id}, {product.name} c:{product.colors}, m:{product.measure}")
    # break_count = 0
    # items = []
    # try:
    #     with transaction.atomic():
    #         for o in order:
    #             order_products = OrderProduct.objects.filter(order=o, product_id__in=cancelled_pro_id)
    #             if order_products:
    #                 break_count += 1
    #                 # break
    #             if not order_products:
    #                 order_product = OrderProduct.objects.filter(order=o)
    #                 if order_product.count() > 1:
    #                     items.append(list(order_product.values("product__name", 'product_variable', 'product__is_collection')))
    # except IntegrityError as e:
    #     return JsonResponse({"count": e}, safe=False)
    # order = Order.objects.filter(id__in=[1, 2, 7, 8], operator_order_id__isnull=False)

    # order = Order.objects.filter(status__in=[1, 2, 7, 8], driver__isnull=False,operator_order_id__isnull=False)
    # for o in order:
    #     o.update_driver_fee()

    # try:
    #     with transaction.atomic():
    #         order_product = OrderProduct.objects.filter(Q(input_price=0)|Q(input_price=None), type='2', status__in=[4, 6], order__output_product__isnull=False, driver__isnull=False)
    #         for o in order_product:
    #             input_product = InputProductItems.objects.filter(product=o.product, updated_at__lte=o.updated_at, price__gt=0).exclude(price=None).order_by("-id")
    #             if not input_product:
    #                 input_product = InputProductItems.objects.filter(product=o.product, updated_at__gte=o.updated_at, price__gt=0).exclude(price=None).order_by("id")

    #             input_price = input_product.first()
    #             if input_price:
    #                 o.input_price=input_price.price
    #                 o.save()
    # except IntegrityError as e:
    #     return JsonResponse({"res1":e, "res2":0, "history":2}, safe=False)

    # driver_hand_product_price = OrderProduct.objects.filter(type__in=[1, 2],status__in=[4, 6], driver__isnull=False, input_price=0).values("product__name","input_price")

    # from warehouse.models import WarehouseOperationItemDetails
    # driver_hand_product_price = OrderProduct.objects.filter(type__in=[1, 3], status__in=[4, 6], driver__isnull=False,
    #                                                         input_price=0).order_by('-order__operator_order_id').values("order_id", "order__operator_order_id", 'product__name', 'type')

    # from warehouse.models import WarehouseOperationItemDetails
    # driver_hand_product_price = OrderProduct.objects.filter(type__in=[2, 1], status__in=[4, 6], driver__isnull=False,
    #                                                         input_price=0, order__output_product__isnull=False).values("order_id", "order__operator_order_id", 'product__name', 'type')

    # details_l = []

    # for o in driver_hand_product_price:
    #     # details = WarehouseOperationItemDetails.objects.filter(order_product=o).aggregate(
    #     #     t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("amount"), output_field=models.IntegerField())), 0))[
    #     #     't']

    #     details = WarehouseOperationItemDetails.objects.filter(order_product=o).values("id")
    #     details_l.append(list(details))
    #     if details > 0:
    #         details_l.append(o.id)
    #         o.input_price=details
    #         o.save()

    # order = Order.objects.filter(status=1, driver__isnull=False).update(driver=None)
    # return JsonResponse({ 'break_count':list(details_l), 'len':len(details_l)}, safe=False)
    la = WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=395).values("id", 'order_id')
    from services.warehouse.purchase.purchase_services import PurchaseProductServices

    purchase_product_services = PurchaseProductServices()
    status_by_collection_product_list = purchase_product_services.get_collections(7)
    return JsonResponse({'break_count': 0, 'data': list(status_by_collection_product_list)}, safe=False)

    # OrderProduct.objects.filter(type__in=[1,2], order__operator_order_id__isnull=False, price=0, order__status=3).update(price=F("unit_price"))
    # 788011
    # OrderProduct.objects.filter(type__in=[1,2], order__operator_order_id__isnull=False, price=0).exclude(order__status__in=[4, 0]).update(price=F("unit_price"))
    # order_pro = OrderProduct.objects.filter(type__in=[1,2], order__operator_order_id__isnull=False, price=0).exclude(order__status__in=[0]).values("id", "order_id","type", "order__status", "order__site", "product__name",
    # "ordered_amount",  "unit_price", "price", "delivery_cost")

    # order = Order.objects.filter(status=2, driver=None).values("id", "customer_region_id")

    # ac_count = 0
    # break_count = 0
    # accepted_pro_id = []
    # for o in order:
    #     order_products = OrderProduct.objects.filter(order=o, product_id__in=cancelled_pro_id)
    #     if order_products:
    #         break_count += 1
    #         # break
    #     if not order_products:
    #         for item in OrderProduct.objects.filter(order=o):
    #             ac_count += 1
    #             product = item.product
    #             accepted_pro_id.append(f"id : {product.id}, {product.name} c:{product.colors}, m:{product.measure}")
    # return JsonResponse({"count":ac_count, 'break_count':break_count, 'ac_count':accepted_pro_id}, safe=False)
    # from datetime import timedelta
    # from django.utils import timezone
    #
    # # Şu anki zamanı alın
    # now = timezone.now()
    #
    # # 4 gün önceki zamanı hesaplayın
    # four_days_ago = now - timedelta(days=4)
    # # Order.objects.filter(status=1, created_at__lt=four_days_ago).update(driver=None, delete_desc="Eskirib qolgani uchun", responsible_id=1, status=0, is_site_change=False)
    # order = Order.objects.filter(id__in=[1, 2, 7, 8], operator_order_id__isnull=False)
    # for o in order:
    #     o.update_driver_fee()

    # order = Order.objects.filter(status=1, created_at__lt=four_days_ago).values("id", 'created_at')
    return JsonResponse({"count": [], 'order': []}, safe=False)

    #     for order_product in order_products:
    #         product = order_product.product
    #         if order_product.product.is_collection is False:
    #           varb = ProductVariable.objects.filter(product=product, is_active=True).count()
    #           if varb != 1:
    #             #   break_name.append(product.id)
    #               break_count += 1
    #               break

    #         else:
    #             collection_items = ProductCollectionItem.objects.filter(product=product)
    #             if not collection_items:
    #                 # break_name.append(product.id)
    #                 break_count += 1
    #                 break
    #             for product_item in collection_items.first().collection.all():
    #                 varb = ProductVariable.objects.filter(product=product_item, is_active=True).count()
    #                 if varb != 1:
    #                     break_name.append(product.id)
    #                     break_count += 1
    #                     break
    #         checked_pro_name.append(f'id:{product.id} - {product.name}')
    #         checked_count += 1
    # return JsonResponse({"count":checked_count, 'break_count':break_count, 'break_name':list(set(break_name))}, safe=False)


def developments(request):
    # warehouse_operations = get_object_or_404(WarehouseOperation, id=warehouse_operation_id)
    # orders_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=warehouse_operation_id).values_list("order_id", flat=True))
    # order = Order.objects.filter(id__in=orders_id)
    #     return JsonResponse({"count":0, "res2":ab, "order_product":order_list}, safe=False)

    # pro = Product.objects.filter(bonus_type="2").update(bonus=0)

    # pro = Product.objects.filter(bonus_type="2").update(bonus=0)
    # pro = Product.objects.filter(measure__isnull=True, is_active=True)
    # for i in pro:
    #     if not i.colors.exists():
    #         variable = ProductVariable.objects.filter(product=i, is_active=False).update(is_active=True)

    # date = datetime.datetime(2024, 2, 3, 23,59)
    datas = []
    # driver_hand_product_price = \
    # OrderProduct.objects.filter(updated_at__lte=date, status__in=[4, 6], driver__isnull=False).exclude(
    #     order__status=4).aggregate(t=Coalesce(Sum(F('ordered_amount') * F('input_price')), 0))['t']

    # driver_hand_product_pricess = \
    # OrderProduct.objects.filter(updated_at__lte=date, status__in=[4, 6], driver__isnull=False).exclude(order__status=4).aggregate(
    #     t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("ordered_amount"), output_field=models.IntegerField())),
    #               0))['t'] or 0

    # # orders = list(Order.objects.filter(site='1', operator_order_id__isnull=False, status__in=[1, 2], site_order_id__isnull=False).values_list("site_order_id", flat=True))

    # return JsonResponse({"order_count":[1], "response":driver_hand_product_price,'res2':driver_hand_product_pricess}, safe=False)

    # fee_operaotr_app = Order.objects.filter(status=4, driver_id=driver_id, operator_order_id__isnull=False).aggregate(
    #     t=Coalesce(Sum("driver_fee"), 0))['t']

    # debttt = \
    # OrderProduct.objects.filter(order__status=4, status=4, driver_id=driver_id, updated_at__year=2024, updated_at__month=2, updated_at__day=1).values("order_id","updated_at", "created_at", "price")

    # debt = \
    # OrderProduct.objects.filter(order__status=4, status=4, driver_id=driver_id).exclude(order_id__in=[701410, 703574, 695616, 700845, 703735, 696588, 697176, 697004, 702232, 702999, 696409, 702646, 695477]).aggregate(
    #     t=Coalesce(Sum("price"), 0))['t']

    # fee = Order.objects.filter(status=4, driver_id=driver_id).aggregate(
    #     t=Coalesce(Sum("driver_fee"), 0))['t']

    # cash = Cash.objects.filter(from_user_id=driver_id).aggregate(t=Coalesce(Sum("amount"), 0))['t']
    # pay_old = DriverPayment.objects.filter(user_id=driver_id).aggregate(t=Coalesce(Sum("amount"), 0))['t']

    # order statusni
    driver_id = 127
    # or_pro = OrderProduct.objects.filter(order__status=4, status=4, driver_id=driver_id).exclude(order__driver_id=driver_id).update(driver_id=127)

    # or_pro = OrderProduct.objects.filter(order__status=4, status=4, driver_id=driver_id, id__in=err).exclude(order_id__in=[701410, 703574, 695616, 700845, 703735, 696588, 697176, 697004, 702232, 702999, 696409, 702646, 695477]).values("order_id", 'driver_id', "order__driver_id",'order__site', 'product__name', 'product_variable','created_at', 'updated_at', 'price', 'order__updated_at', 'order__created_at')

    # output_product _ id = 11303
    # driver_id = 267

    # import datetime
    # out = OutputProduct.objects.filter(id=11303).update(driver_id=267, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
    #

    # shipping_start data ni yangilash  driver_id yangilash
    # orders = list(Order.objects.filter(output_product_id=11303).values_list("id", flat=True))

    # orders = list(Order.objects.filter(output_product_id=11303).update(driver_id=267, driver_shipping_start_date=datetime.datetime.now())

    my_l = [
        695255,
        695266,
        695296,
        695308,
        695452,
        695699,
        695750,
        695931,
        696186,
        696198,
        696199,
        696715,
        697088,
        697090,
        697110,
        697498,
        697673,
        697677,
        697689,
        698951,
        699030,
        699031,
        699310,
        699538,
        699651,
        699911,
        700106,
        700615,
        700699,
        701121,
        701132
    ]

    # import datetime
    # out = OutputProduct.objects.filter(id=11303).update(driver_id=267, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
    # OrderProduct.objects.filter(order_id__in=my_l).update(status=4)
    # orders = Order.objects.filter(output_product_id=11303).update(driver_id=267, driver_shipping_start_date=datetime.datetime.now())
    # or_pro = OrderProduct.objects.filter(status=3).values("order_id", "order__operator_order_id", "order__site_order_id", 'order__status','status','driver_id', "driver__first_name", "driver__last_name", "order__driver_id", "order__driver__first_name", "order__driver__last_name",'order__site', 'product__name', 'product_variable','created_at', 'updated_at', 'price', 'order__updated_at', 'order__created_at')

    # balance = debt - fee - (cash + pay_old)  values("order_id","price")  order__status=5, [4, 3, 5, 6, 2]
    # driver_id sini yangilash
    # or_pro = OrderProduct.objects.filter(driver__isnull=False, order__driver__isnull=False).exclude(order__driver_id=F("driver_id")).values("order_id", "order__operator_order_id", "order__output_product","order__site_order_id", 'order__status','status','driver_id', "driver__first_name", "driver__last_name", "order__driver_id", "order__driver__first_name", "order__driver__last_name",'order__site', 'product__name', 'product_variable','created_at', 'updated_at', 'price', 'order__updated_at', 'order__created_at')
    # or_pro = OrderProduct.objects.filter(driver__isnull=False, order__driver__isnull=False).exclude(order__driver_id=F("driver_id")).values("order_id", "order__customer_phone", "order__customer_name", 'amount','product__name')
    # or_pro = OrderProduct.objects.filter(driver__isnull=False, order__driver__isnull=False).exclude(order__driver_id=F("driver_id")).values("order_id", "order__operator_order_id", "order__site_order_id", 'order__status','status','driver_id', "driver__first_name", "driver__last_name", "order__driver_id", "order__driver__first_name", "order__driver__last_name",'order__site', 'product__name', 'product_variable','created_at', 'updated_at', 'price', 'order__updated_at', 'order__created_at')
    # appa = OrderProduct.objects.filter(driver__isnull=False, order__driver__isnull=False, order__status=5).exclude(order__driver_id=F("driver_id"))
    # or_pro = OrderProduct.objects.filter(order__status=4, status=4, driver_id=driver_id).exclude(order__driver_id=driver_id).values("order_id", 'driver_id', "driver__first_name", "driver__last_name", "order__driver_id", "order__driver__first_name", "order__driver__last_name",'order__site', 'product__name', 'product_variable','created_at', 'updated_at', 'price', 'order__updated_at', 'order__created_at')
    # or_proa = OrderProduct.objects.filter(order__status=4, status=4, driver__isnull=False, order__driver__isnull=False).exclude(order__driver_id=F("driver_id"))

    # or_pro = []
    # or_pros = OrderProduct.objects.filter(order__status=3, driver__isnull=False, order__driver_id=1980).exclude(order__driver_id=F("driver_id")).update(driver_id=1980, status=4)
    # appa = OrderProduct.objects.filter(order__status__in=[3,6, 5], status=4, driver__isnull=False, order__driver__isnull=False).exclude(order__driver_id=F("driver_id"))

    # from datetime import datetime

    # # 2024 yılının Ocak ayının ilk günü ve son günü
    # start_date = datetime(2024, 1, 1)
    # end_date = datetime(2024, 1, 31, 23, 59, 59)
    # seller_Fee = Order.objects.filter(site=2, status=4, site_order_id__isnull=False, updated_at__date__range=(start_date, end_date)).aggregate(t=Coalesce(Sum("seller_fee"), 0))['t']

    # for a in appa:
    #     a.driver_id=a.order.driver_id
    #     a.save()
    # datas

    # from datetime import datetime

    # ora = Order.objects.filter(status=5, site=1,site_order_id__in=datas).values("id", 'site_order_id',"updated_at", "is_site_change","seller_fee").order_by("-updated_at")
    # ora_id = Order.objects.filter(status=5, site=1,site_order_id__in=datas).values_list("site_order_id", flat=True).order_by("-updated_at")

    # new_list = []
    # for i in my_data:
    #     order = Order.objects.filter(site=1, site_order_id=i['id']).first()
    #     if order:
    #         new_list.append({"id":i['id'], "site_updated_at":i['update_at'], 'el_updated_at':order.updated_at})
    # return JsonResponse({"result":[1]}, safe=False)

    filtered_data = []
    # for item in new_list:
    #     site_updated_at_str = item["site_updated_at"]
    #     el_updated_at_str = item["el_updated_at"]

    #     try:
    #         # Dönüştürmeyi strptime ile yapın
    #         site_updated_at = datetime.strptime(site_updated_at_str, "%Y-%m-%dT%H:%M:%S.%f")
    #         el_updated_at = datetime.strptime(el_updated_at_str, "%Y-%m-%dT%H:%M:%S.%f")
    #         time_delta = site_updated_at - el_updated_at
    #         if time_delta.days > 1:
    #             filtered_data.append(item)
    #     except ValueError:
    #         # Dönüştürme hatası olursa uyarı verin
    #         print(f"Error converting date for item with ID {item['id']}: {site_updated_at_str} or {el_updated_at_str}")

    from datetime import datetime
    # 10 Kasım 2023 tarihinden sonraki siparişleri çekmek için
    start_date = datetime(2023, 11, 1)

    # order_list = Order.objects.filter(site=1, site_order_id__in=my_variable).exclude(status=5).values("id", "status", "is_site_change","site_order_id","updated_at", "seller_fee")

    from django.db.models import Count

    # site_id'ye göre order'ları gruplayıp, site_order_id'ye göre sıralama

    # ids = [703642, 702035, 656642, 506127, 493390]
    # duble_order = Order.objects.filter(id__in=ids).update(site_order_id=None)
    # orders = Order.objects.filter(order_count__gt=1, site__isnull=False, site_order_id__isnull=False).values('site', 'site_order_id').annotate(order_count=Count('id')).order_by('site', 'site_order_id')

    # duble_order = list(Order.objects.filter(site=1, site_order_id__in=ids, status=4).values_list("site_order_id", flat=True))
    # pro = Product.objects.filter(bonus_type="2").update(bonus=0)

    # pro = Product.objects.filter(bonus_type="2").values("id", "bonus")

    return JsonResponse({'filtered_data': [], 'orders': list(pro)}, safe=False)

    # return JsonResponse({"order_product_total_price":or_pro.aggregate(t=Coalesce(Sum("price"), 0))['t'], "total_count":or_pro.count()}, safe=False)

    # return JsonResponse({"order_count":[1], "debt":debt, "fee":fee, "cash":cash, "pay_old":pay_old, "balance":balance, 'de-------bttt':list(debttt), 'fee_oasdasdasdadperaotr_app':fee_operaotr_app}, safe=False)


def development_old(request):
    # orders = list(Order.objects.filter(site='1', operator_order_id__isnull=False, status__in=[1, 2], site_order_id__isnull=False).values_list("id", flat=True))

    # barcode_in()

    # orders = Order.objects.filter(barcode=3824931808477, status=1).update(barcode=barcode_generate())

    # 3824931808477
    # check_product_variable_order_product()
    # ProductImage.objects.filter(default_image__isnull=False).update(
    #         high_image=F('default_image'),
    #         low_image=F("default_image")
    #     )

    # ProductVariable.objects.all().delete()

    # try:
    #     with transaction.atomic():
    #         order_product = OrderProduct.objects.filter(Q(input_price=0)|Q(input_price=None), status=4, order__status=4)
    #         for o in order_product:
    #             input_product = InputProductItems.objects.filter(product=o.product, updated_at__lte=o.updated_at, price__gt=0).exclude(price=None).order_by("-id")
    #             if not input_product:
    #                 input_product = InputProductItems.objects.filter(product=o.product, updated_at__gte=o.updated_at, price__gt=0).exclude(price=None).order_by("id")

    #             input_price = input_product.first()
    #             if input_price:
    #                 o.input_price=input_price.price
    #                 o.save()
    # except IntegrityError as e:
    #     return JsonResponse({"res1":e, "res2":0, "history":2}, safe=False)

    # order = Order.objects.filter(operator_id=3424).update(operator_id=3369)

    # order = list(Order.objects.filter(status=1).exclude(customer_district__region_id=F('customer_region_id')).values('id', "site_order_id", "created_at", "delivered_date", "customer_region__name", "customer_district__name"))
    l = []
    # product = Product.objects.all()
    # for i in product:
    #         amount = int(i.total_regions_storehouse_amount)
    #         if int(amount) > 0:
    #             input = InputProductItems.objects.filter(product_id=i.id, amount__isnull=False)
    #             l.append({"1":f'etap {i.name}'})
    #             for a in input:
    #                 a_amount =int(a.amount)
    #                 if amount > 0 and a_amount > 0:
    #                     l.append({"2":f'etap {i.name}'})
    #                     if a_amount >= amount:
    #                         InputProductItems.objects.filter(id=a.id).update(amount=a_amount-amount)
    #                         amount = 0

    #                         l.append({"3":f'etap {i.name} miqdori : inputdagi {a_amount} proniki {amount}'})

    #                     else:
    #                         amount = amount - a_amount
    #                         InputProductItems.objects.filter(id=a.id).update(amount=0)
    #                         l.append({"4":f'etap {i.name}'})

    # from store.models import ProductSize
    # sizes = ProductSize.objects.all()
    # for i in sizes:
    #     map = {"mm":3, "cm":2, "kg":1, "gr":3, "l":5, "xl":15}.get(i.type, None)
    #     i.size_type_id = map
    #     i.save()
    # pro_id_lists = [518]
    # order_pro = OrderProduct.objects.filter(product_id__in=pro_id_lists).update(product_id=499, product_item_id=813)
    # OutputProductItems.objects.filter(product_id__in=pro_id_lists).update(product_id=499)
    # InputProductItems.objects.filter(product_id__in=pro_id_lists).update(product_id=499)

    # order_product = set(OrderProduct.objects.filter(product_id=462, order__status=1, order__site=2, order__site_order_id__isnull=False).values_list("order_id", flat=True))
    # order = Order.objects.filter(status=1, site=2, id__in=order_product, site_order_id__isnull=False)
    # url = "https://airshop.uz/api/order-change-satus-from-elituvchi/"
    # response = update_order_status_on_other_sites(1,url, order.values_list("site_order_id", flat=True))
    # from datetime import timedelta
    # today = datetime.date.today() - timedelta(days=1)
    # item = list(OutputProductItems.objects.filter(created_at__day=today.day, created_at__month=today.month, product_id=462).annotate(
    #     driver_phone=F("output_product__driver__username"), total_amount=Sum("amount")
    # ).values("driver_phone", 'total_amount'))

    # op_list = []
    # operator = User.objects.filter(type=3, is_active=True)
    # for i in operator:
    #     op_list.append(i.username)
    # item = list(OutputProductItems.objects.filter(
    #     created_at__day=today.day,
    #     created_at__month=today.month,
    #     product_id=462
    # ).values('output_product__driver__username').annotate(
    #     total_amount=Sum('amount')
    # ))
    # operator = User.objects.filter(type=3, payment_card__isnull=False).update(payment_card=None)
    # re = []
    # for o in operator:
    # re.append({"id":o.id, "username":o.username, "payment_card":o.payment_card})
    # return redirect("https://d.savdo24.com")
    # li = Districts.objects.all().values("id", "region_id", "name")
    # from django.db.models import Q, F, Count

    # duplicate_phone_orders = Order.objects.values('customer_phone').annotate(count=Count('customer_phone', filter=Q(status__in=[1,2,3,6]))).filter(
    #     count__gt=1)
    # cash_transactions1 = Cash.objects.filter(created_at__year=2023, created_at__month='08').values('category', 'category__name').annotate(total_amount=Sum('amount'))
    # cash_transactions2 = Cash.objects.filter(created_at__year=2023, created_at__month='07').values('category', 'category__name').annotate(total_amount=Sum('amount'))
    # cash_transactions3 = Cash.objects.filter(created_at__year=2023, created_at__month='06').values('category', 'category__name').annotate(total_amount=Sum('amount'))

    # l = []

    # date = datetime.datetime(2023, 9, 3)
    # from django.db import models
    # total_ins = Cash.objects.filter(to_user__cashieruser__isnull=False, created_at__lte=date).aggregate(t=Coalesce(models.Sum("amount"), 0))['t']
    # total_outs = Cash.objects.filter(from_user__cashieruser__isnull=False, created_at__lte=date).aggregate(t=Coalesce(models.Sum("amount"), 0))['t']
    # cashier = CashierUser.objects.all()
    # balance = 0
    # history = []
    # for i in cashier:
    #     total_in = Cash.objects.filter(to_user_id=i.user.id).aggregate(t=Coalesce(models.Sum("amount"), 0))['t']
    #     total_out = Cash.objects.filter(from_user_id=i.user.id).aggregate(t=Coalesce(models.Sum("amount"), 0))['t']
    #     history.append({f"{i.user.first_name}":total_in-total_out, 'b':i.balance})
    #     balance = (total_in-total_out) + balance

    # total_in = Cash.objects.filter(to_user_id=i.user.id,created_at__lte=date).aggregate(t=Coalesce(models.Sum("amount"), 0))['t']
    # total_out = Cash.objects.filter(from_user_id=i.user.id, created_at__lte=date).aggregate(t=Coalesce(models.Sum("amount"), 0))['t']

    # total_in = Cash.objects.filter(to_user_id=i.user.id).aggregate(t=Coalesce(Sum("amount"),0))['t']
    # total_out = Cash.objects.filter(from_user_id=i.user.id).aggregate(t=Coalesce(Sum("amount"),0))['t']
    # i.balance=total_in-total_out
    # i.save()
    # print(balance)

    from datetime import datetime

    # 10 Kasım 2023 tarihinden sonraki siparişleri çekmek için
    start_date = datetime(2023, 11, 1)

    order_list = Order.objects.filter(site=1, site_order_id__in=my_variable).exclude(status=5).values("id", "status",
                                                                                                      "updated_at")
    # order_products = OrderProduct.objects.filter(order__status=1, product_id=575, product_variable=None, product__is_collection=True)
    # # err_pro_id= [667, 680, 667, 663, 537, 526, 367, 479, 478, 530, 425, 539, 23, 22]

    # for order_product in order_products:
    #         for collection_item in order_product.product.product_collection_item.all():
    #             collection_item_variable = ProductVariable.objects.filter(product=order_product.product).first()
    #             collection = OrderProductCollectionItem.objects.get_or_create(order_product=order_product, product=order_product.product, product_variable=collection_item_variable)

    order_products = OrderProduct.objects.filter(order__status=1, product_id=575, product_variable=None,
                                                 product__is_collection=True)
    # err_pro_id= [667, 680, 667, 663, 537, 526, 367, 479, 478, 530, 425, 539, 23, 22]
    from order.models import Order, OrderProductCollectionItem

    from store.models import ProductCollectionItem
    for order_product in order_products:

        collection = ProductCollectionItem.objects.get(product_id=575)
        # for collection_item in order_product.product.product_collection_item.all():
        for c in collection.collection.all():
            collection_item_variable = ProductVariable.objects.filter(product=c.id).first()
            collection = OrderProductCollectionItem.objects.get_or_create(order_product=order_product, product_id=c.id,
                                                                          product_variable=collection_item_variable)

    ab = []
    # order_products = OrderProduct.objects.filter(Q(product__colors__isnull=False)|Q(product__measure__isnull=False), order__status=1, product__is_collection=False)
    # order_products = OrderProduct.objects.filter(order__status=1, product__is_collection=True)

    # for c in order_products:
    #     ab.append({'product_id':c.product.id, 'order_id':c.order_id,'desc':c.order.customer_street, 'name':c.product.name,})

    # return JsonResponse({"count":0, "res2":ab, "order_product":order_products.count()}, safe=False)
    return JsonResponse({"count": 0, "res2": ab, "order_product": order_list}, safe=False)


@login_required(login_url='/login')
def home(request):
    if request.user.type == "2":
        messages.success(request, "Xush kelibsiz")
        return redirect("driver_app_profile")
    if request.user.type == "4":
        messages.success(request, "Xush kelibsiz")
        return redirect("seller_app_profile")
    if request.user.type == "3":
        messages.success(request, "Xush kelibsiz")
        return redirect("operator_app_profile")



    sync_permission = request.GET.get("sync_permission")
    if sync_permission and request.user.is_superuser:
        from config.permission import sync_permission
        sync_permission()
        messages.success(request, "Sinxronlandi")
        return redirect("home")

    return render(request, 'home/index.html')


@login_required(login_url='/login')
def change_color(request):
    user = User.objects.get(id=request.user.id)
    if user.theme == '1':
        change(user, '2')
    elif user.theme == '2' or user.theme == None:
        change(user, '1')
    return JsonResponse({'status': "true"})


def change(user, type):
    user.theme = type
    user.save()


def my_custom_page_not_found_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '404 page not found'})


def my_custom_error_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '500 server error'})


def my_custom_permission_denied_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '403 peremission denied'})


def my_custom_bad_request_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '400 bad request'})
