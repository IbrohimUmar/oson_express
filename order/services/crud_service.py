import logging

from store.models import ProductVariable
from store.services.product_feature import ProductFeatureService

developer_logger = logging.getLogger('developer_logger')





"""
 Orderni edit qilishda esdan chiqarmaslik
 1. statusi


"""
from django.db import transaction, IntegrityError

from config.barcode import barcode_generate
from order.models import Order, OrderProduct
from config.settings.base import  TOLL_AMOUNT


class OrderCrudService:

    def get_order_product_product_json(self, order_id):
        order_products = OrderProduct.objects.filter(product_type__in=[1, 2], order_id=order_id)
        selected_products_list = []
        for item in order_products:
            product = item.product
            product_variable = item.product_variable
            product_feature_services = ProductFeatureService(product)

            main_data = {
                "order_product_id": item.id,
                "global_id": product.id,
                "name": product.name,

                "total_price": item.total_price,
                "price": item.unit_price,
                "standard_price": item.unit_price,

                "discount": item.bonus_from_price if item.bonus_from_price is not None else 0,

                "toll": TOLL_AMOUNT if item.is_delivery_free is False else 0,
                "pay_toll": item.delivery_cost if item.delivery_cost is None else 0,

                "give_bonus_amount": item.bonus_from_quantity,

                "amount": item.quantity,
                "total_amount": item.total_quantity,

                "selected_color": {},
                "selected_measure_item": {},
                "selected_product_variable": {},
                "selected_product_variable_id": product_variable.id if product_variable is not None else None,

                "is_collection": product.is_collection,
                "bonus_type": product.bonus_type,
                "bonus_details": product_feature_services.product_bonus_details,
            }

            if product.is_collection is False:
                feature = product_feature_services.get_features
                main_data.update(feature)

                if product_variable is not None and product_variable.color is not None:
                    main_data["selected_color"] = {"id": product_variable.color.id, "name": product_variable.color.name,
                                                   "color": product_variable.color.color, "on_sale": True}

                if product_variable is not None and product_variable.measure_item is not None:
                    main_data["selected_measure_item"] = {"id": product_variable.measure_item.id,
                                                          "name": product_variable.measure_item.name, "on_sale": True}

                if product_variable is not None:  # variable tanlanmagan donali mahsulot bo'lsa break
                    product_variable_values = ProductVariable.objects.filter(id=product_variable.id).values("id",
                                                                                                            "color__name",
                                                                                                            "color_id",
                                                                                                            "measure_item__name",
                                                                                                            "measure_item_id",
                                                                                                            "is_active",
                                                                                                            "is_different_price",
                                                                                                            "price")
                    if product_variable_values.exists():
                        main_data["selected_product_variable"] = product_variable_values[0]

            elif product.is_collection is True:
                collection = []
                selected_collection_queryset = OrderProduct.objects.filter(product_type='3',
                                                                           main_order_product_id=item.id)
                if len(selected_collection_queryset) < 2:
                    continue
                for s in selected_collection_queryset:
                    collection_item_feature = ProductFeatureService(s.product)
                    collection_data = collection_item_feature.get_collection_item_features
                    if s.product_variable:
                        # variable = ProductVariable.objects.get(id=s.product_variable.id)
                        variable = s.product_variable
                        collection_data['selected_product_variable'] = {
                            "id": variable.id,
                            "color__name": variable.color.name if variable.color is not None else None,
                            "color_id": variable.color_id,
                            "measure_item__name": variable.measure_item.name if variable.measure_item is not None else None,
                            "measure_item_id": variable.measure_item_id,
                            "is_active": variable.is_active,
                            "is_different_price": variable.is_different_price,
                            "price": variable.price
                        }
                        if variable.color:
                            collection_data['selected_color'] = {"id": variable.color.id, "name": variable.color.name,
                                                                 "color": variable.color.color}

                        if variable.measure_item:
                            collection_data['selected_measure_item'] = {"id": variable.measure_item.id,
                                                                        "name": variable.measure_item.name}
                    else:
                        collection_data['selected_product_variable'] = {}
                        collection_data['selected_color'] = {}
                        collection_data['selected_measure_item'] = {}
                    collection.append(collection_data)
                # collection = product_feature_services.get_collection_all_item_list
                if collection is None:
                    continue
                main_data['collection_items'] = collection
            selected_products_list.append(main_data)
        return selected_products_list

    def order_edit(self, order):
        pass



    def order_products_edit(self, order):
        pass


    def order_product_create(self, order, products_json):
        for p in products_json:
            if p['is_collection']:
                main_order_product = OrderProduct.objects.create(
                    order=order,
                    product_type='2',
                    product_id=p['global_id'],

                    unit_price=p['price'],
                    total_unit_price=p['price'] * p['amount'],
                    total_price=p['total_price'],

                    bonus_type=p['bonus_type'],
                    bonus_condition=p['bonus_details']['bonus'],
                    bonus_condition_quantity=p['bonus_details']['bonus_amount'],

                    quantity=p['amount'],
                    total_quantity=p['total_amount'],

                    bonus_from_price=p['discount'],
                    bonus_from_quantity=p['give_bonus_amount'],

                    delivery_cost=p['pay_toll'],
                    is_delivery_free=False if int(p['pay_toll']) > 0 else True,

                )
                for collection_item in p['collection_items']:
                    OrderProduct.objects.create(
                        order=order,
                        product_type='3',
                        product_id=collection_item['global_id'],
                        main_order_product=main_order_product,
                        product_variable_id=collection_item['selected_product_variable']['id'],
                        is_delivery_free=True,
                    )
            else:
                unit_order_product = OrderProduct.objects.create(
                    order=order,
                    product_type='1',
                    product_id=p.get('global_id', p.get('id', None)),
                    unit_price=p['price'],
                    total_unit_price=p['price'] * p['amount'],
                    total_price=p['total_price'],

                    product_variable_id=p['selected_product_variable']['id'],

                    bonus_type=p['bonus_type'],
                    bonus_condition=p['bonus_details']['bonus'],
                    bonus_condition_quantity=p['bonus_details']['bonus_amount'],

                    quantity=p['amount'],
                    total_quantity=p['total_amount'],

                    bonus_from_price=p['discount'],
                    bonus_from_quantity=p['give_bonus_amount'],

                    delivery_cost=p['pay_toll'],
                    is_delivery_free=False if int(p['pay_toll']) > 0 else True,
                )

    def order_create_from_operator(self, operator_order, operator_fee_amount):
        try:
            with transaction.atomic():
                order = Order.objects.create(operator=operator_order.operator,
                                             site=operator_order.site,
                                             barcode=barcode_generate(),
                                             site_order_id=operator_order.site_order_id,
                                             customer_name=operator_order.customer_name[:50],
                                             customer_phone=operator_order.customer_phone[:30],
                                             customer_phone2=operator_order.customer_phone2[:30],

                                             customer_region=operator_order.region,
                                             customer_district=operator_order.district,
                                             customer_street=operator_order.street,

                                             seller_fee=operator_order.seller_fee,
                                             operator_fee=operator_fee_amount,

                                             order_date=operator_order.created_at.strftime(("%Y-%m-%d")),
                                             delivered_date=operator_order.delivery_date,
                                             status=1,

                                             operator_order_id=operator_order.id,

                                             driver_is_bonus=operator_order.district.driver_is_bonus,
                                             driver_one_day_bonus=operator_order.district.driver_one_day_bonus,
                                             driver_two_day_bonus=operator_order.district.driver_two_day_bonus,
                                             )
                # operator_order_items = OperatorOrderItem.objects.filter(order=operator_order)
                # order_items = []
                # for operator_order_item in operator_order_items:
                #     if operator_order_item.order_type == '1':
                #         order_items.append(
                #             OrderProduct(status=1,
                #                          type="1",
                #                          order_id=order.id,
                #                          product=operator_order_item.product,
                #                          product_variable=operator_order_item.product_variable,
                #
                #                          ordered_amount=operator_order_item.total_amount,
                #                          price=operator_order_item.total_price,
                #
                #                          bonus_from_amount=operator_order_item.bonus_from_amount,
                #                          bonus_from_price=operator_order_item.bonus_from_price,
                #
                #                          is_delivery_free=operator_order_item.is_delivery_free,
                #                          delivery_cost=operator_order_item.delivery_cost,
                #                          only_ordered_amount=operator_order_item.amount,
                #                          unit_price=operator_order_item.price,
                #                          )
                #         )
                #     elif operator_order_item.order_type == '2':
                #         operator_order_collection_items = OrderCollectionItem.objects.filter(
                #             order_item=operator_order_item)
                #         product_collection_create = OrderProduct.objects.create(
                #             status=1, type="2",
                #             order_id=order.id,
                #             product=operator_order_item.product,
                #             product_variable=operator_order_item.product_variable,
                #
                #             ordered_amount=operator_order_item.total_amount,
                #             price=operator_order_item.total_price,
                #
                #             bonus_from_amount=operator_order_item.bonus_from_amount,
                #             bonus_from_price=operator_order_item.bonus_from_price,
                #
                #             is_delivery_free=operator_order_item.is_delivery_free,
                #             delivery_cost=operator_order_item.delivery_cost,
                #             only_ordered_amount=operator_order_item.amount,
                #             unit_price=operator_order_item.price,
                #         )
                #         for operator_order_collection_item in operator_order_collection_items:
                #             order_items.append(
                #                 OrderProduct(status=1,
                #                              type="3",
                #                              main_order_product=product_collection_create,
                #
                #                              order_id=order.id,
                #                              product=operator_order_collection_item.product,
                #                              product_variable=operator_order_collection_item.product_variable,
                #
                #                              only_ordered_amount=0,
                #                              ordered_amount=0,
                #                              price=0,
                #
                #                              is_delivery_free=True,
                #                              delivery_cost=0,
                #                              unit_price=0,
                #                              )
                #             )
                    # print(i)
                # OrderProduct.objects.bulk_create(order_items)
                order.update_driver_fee()
                return True
        except IntegrityError as e:
            developer_logger.error(str(f"createOrderFromOtherSitesError {str(e)}"), exc_info=True)
            raise IntegrityError
