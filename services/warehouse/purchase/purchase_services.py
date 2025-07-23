from django.db import transaction
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce

from order.models import OrderProduct
from warehouse.models import WarehouseOperationItemDetails, WareHouseStock


class PurchaseProductServices:

    def get_warehouse_stock_amount(self, warehouse_id, product_variable_id):
        main_warehouse = WareHouseStock.objects.filter(warehouse_id=warehouse_id,
                                                       product_variable_id=product_variable_id).first()
        if main_warehouse:
            if warehouse_id == 1:
                return main_warehouse.attachment_amount
            return main_warehouse.amount
        return 0


    def compare_dicts(self, dict1, dict2):
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        if keys1 != keys2:
            return False
        for key in keys1:
            if dict1[key] != dict2[key]:
                return False
        return True




    def get_collections(self, order_status):
        # main_collections = OrderProduct.objects.filter(order__status=order_status, type=2).order_by("product_id").values("id", 'ordered_amount', 'product_id', 'product__name')
        # collections = {}

        # variable_items_dict = {}
        # for item in OrderProduct.objects.filter(type=3, order__status=order_status).values("main_order_product_id",
        #                                                                                   "product_id",
        #                                                                                   'product_variable_id',
        #                                                                                   'product__name',
        #                                                                                   'product_variable__color__name',
        #                                                                                   'product_variable__measure_item__name'):
        #     main_order_product_id = item["main_order_product_id"]
        #     if main_order_product_id not in variable_items_dict:
        #         variable_items_dict[main_order_product_id] = []
        #     variable_items_dict[main_order_product_id].append(item)

        # for main_collection in main_collections:
        #     item_map = {item['product_id']: item['product_variable_id'] for item in variable_items_dict.get(main_collection['id'], [])}
        #     existing_collection = collections.get(main_collection['product_id'])
        #     if existing_collection is None:
        #         collections[main_collection['product_id']] = [{
        #             "collection_items_product_variable": item_map,
        #             "total_amount": main_collection['ordered_amount'],
        #             "queryset": main_collection,
        #             "variables": variable_items_dict.get(main_collection['id'], []),
        #         }]
        #     else:
        #         for c in existing_collection:
        #             result = self.compare_dicts(c['collection_items_product_variable'], item_map)
        #             if result:
        #                 c['total_amount'] += main_collection['ordered_amount']
        #             else:
        #                 existing_collection.append({"collection_items_product_variable": item_map,
        #                                   "total_amount": main_collection['ordered_amount'],
        #                                   'queryset':main_collection,
        #                                     "variables": variable_items_dict.get(main_collection['id'], []),
        #                                             })
        # main_order_product = []
        # for d in collections.values():
        #     for a in d:
        #         main_order_product.append(a)
        # return main_order_product
        return []

    def get_unit_product_and_collection(self, order_status=1, order_region=None):
        if order_region:
            return list(
                OrderProduct.objects.filter(product_type__in=[1, 2], order__status=order_status, order__customer_region_id=order_region).values(
                    "product__name", "product_variable__color__name", "type",
                    "product_variable__measure_item__name").annotate(
                    total_count=Coalesce(Sum("total_quantity"), 0),
                ).order_by('-total_count'))

        order_product = list(
            OrderProduct.objects.filter(product_type__in=[1, 2], order__status=order_status).values(
                "product__name", "product_variable__color__name", "type",
                "product_variable__measure_item__name").annotate(
                total_count=Coalesce(Sum("total_quantity"), 0),
            ).order_by('-total_count'))
        return order_product

    # def get_collections(self, order_status):
    #     main_collections = OrderProduct.objects.filter(order__status=order_status, type=2).order_by("product_id").values("id", 'ordered_amount', 'product_id')
    #     collections = {}
    #     for main_collection in main_collections:
    #         # Map item IDs to product variable IDs
    #         item_map = {item['product_id']: item['product_variable_id'] for item in OrderProduct.objects.filter(type=3, order__status=order_status,
    #                                                       main_order_product_id=main_collection['id']).values("product_id", 'product_variable_id')}
    #         existing_collection = collections.get(main_collection['product_id'])
    #         if existing_collection is None:
    #             collections[main_collection['product_id']] = [{
    #                 "collection_items_product_variable": item_map,
    #                 "amount": main_collection['ordered_amount'],
    #                 "example_order_product_id": main_collection['id']
    #             }]
    #         else:
    #             for c in existing_collection:
    #                 result = self.compare_dicts(c['collection_items_product_variable'], item_map)
    #                 if result:
    #                     c['amount'] += main_collection['ordered_amount']
    #                 else:
    #                     existing_collection.append({"collection_items_product_variable": item_map,
    #                                       "amount": main_collection['ordered_amount'],
    #                                       'example_order_product_id':main_collection['id']})
    #     main_order_product = []
    #     for d in collections.values():
    #         for a in d:
    #             a['queryset'] = OrderProduct.objects.get(id=a['example_order_product_id'])
    #             main_order_product.append({"queryset":OrderProduct.objects.get(id=a['example_order_product_id']), 'total_amount':a['amount'], 'ordered_product_id':a['example_order_product_id']})
    #     return main_order_product


    def get_unit_product_variable_list(self, order_status=1):
        order_product = list(
            OrderProduct.objects.filter(product_type=1, order__status=order_status, product_variable__isnull=False).values(
                "product_variable_id", "product__name", "product_variable__color__name",
                "product_variable__measure_item__name", "total_quantity").order_by('-total_quantity'))
        return order_product


    def get_product_variable_list(self, order_status=1, order_region=None):
        if order_region:
            return list(
                OrderProduct.objects.filter(product_type__in=[1, 3], order__status=order_status, product_variable__isnull=False, order__customer_region_id=order_region).values(
                    "product_variable_id", "product__name", "product_variable__color__name",
                    "product_variable__measure_item__name").annotate(
                    unit_count=Coalesce(Sum("total_quantity", filter=Q(product_type="1")), 0),
                    collection_count=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type="3")), 0),
                    total_count=F("unit_count") + F("collection_count")
                ).order_by('-total_count'))        
        order_product = list(
            OrderProduct.objects.filter(product_type__in=[1, 3], order__status=order_status, product_variable__isnull=False).values(
                "product_variable_id", "product__name", "product_variable__color__name",
                "product_variable__measure_item__name").annotate(
                    unit_count=Coalesce(Sum("total_quantity", filter=Q(product_type="1")), 0),
                    collection_count=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type="3")), 0),
                    total_count=F("unit_count") + F("collection_count")
            ).order_by('-total_count'))
        return order_product



    @property
    def get_product_waited_product_variable_count(self):
        order_product = self.get_product_variable_list()

        variables_list = [i['product_variable_id'] for i in order_product]

        main_warehouse_results = {w['product_variable_id']: w['attachment_amount'] for w in WareHouseStock.objects.filter(warehouse_id=1, product_variable_id__in=variables_list,
                                                        attachment_amount__gt=0).values("product_variable_id", "attachment_amount")}

        for o in order_product:

            warehouse_attachment_amount =  main_warehouse_results.get(o['product_variable_id'], 0)
            total_order_product_amount = o['total_count']
            need_to_buy = total_order_product_amount
            take_china_warehouse_amount = 0



            if need_to_buy > warehouse_attachment_amount:
                need_to_buy -= warehouse_attachment_amount
            elif need_to_buy < warehouse_attachment_amount:
                need_to_buy = 0

            o['warehouse_attachment_amount'] = warehouse_attachment_amount
            o['need_to_buy'] = need_to_buy
            o['take_china_warehouse_amount'] = take_china_warehouse_amount

        return order_product




