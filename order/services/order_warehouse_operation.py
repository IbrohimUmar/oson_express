from config.seller_app.warehouse.services import warehouse_operation_manager
from config.seller_app.warehouse.services.warehouse_operation_item_manager import WarehouseOperationItemManager
from config.seller_app.warehouse.services.warehouse_operation_item_details_manager import WarehouseOperationItemDetailsManager
from order.models import Order
from services.order.history import save_order_status_history

from warehouse.models import WareHouse, WarehouseOperationAndOrderRelations
from config.seller_app.warehouse.services.warehouse_stock_manager import WarehouseStockManager
from warehouse.models import WareHouseStock
from order.models import OrderProduct
import datetime
from django.db.models import Sum
from django.db.models.functions import Coalesce
from config.seller_app.warehouse.services.warehouse_operation_manager import WarehouseOperationManager


class InsufficientStockError(Exception):
    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"{product_name} shu mahsulotdan omborda yetarli emas.")



class OrderWarehouseOperationsService:

    def _warehouse_operation_and_order_relations_get_orders_id(self, warehouse_operation):
        orders_id = list(
            WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation=warehouse_operation).values_list("order_id",
                                                                                                          flat=True))
        return orders_id


    def driver_send_product_cancel(self, warehouse_operation, responsible=None):
        orders_id = self._warehouse_operation_and_order_relations_get_orders_id(warehouse_operation)
        # Order.objects.filter(id__in=orders_id).update(status=1)
        for o in Order.objects.filter(id__in=orders_id):
            o.status = 1
            o.save()
            save_order_status_history(o, o.status, "Buyurtma hodim tarafidan qabul qilindiga olindi",
                                      responsible,
                                      'config.warehouse.services.order_warehouse_operation')


    def driver_send_product_accept(self, warehouse_operation, responsible=None):
        orders_id = self._warehouse_operation_and_order_relations_get_orders_id(warehouse_operation)
        Order.objects.filter(id__in=orders_id).update(status=3, cancelled_status="1",
                                                      driver_shipping_start_date=datetime.datetime.today().strftime(("%Y-%m-%d")),
                                                      updated_at=datetime.datetime.today())

            
        # for o in OrderProduct.objects.filter(product_type__in=[1, 3], order_id__in=orders_id):
        #     input_price_total = WarehouseOperationItemDetails.objects.filter(order_product=o).aggregate(
        #             t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("amount"), output_field=models.IntegerField())), 0))['t']
        #     o.total_input_price = input_price_total
        #     o.save()


        for o in Order.objects.filter(id__in=orders_id):
            o.total_product_input_price = OrderProduct.objects.filter(order=o, product_type__in=[1,3]).aggregate(t=Coalesce(Sum("total_input_price"), 0))['t']
            o.save()
            o.update_driver_fee()
            save_order_status_history(o, o.status, "Buyurtma hodim tarafidan yetkazilmoqdaga olindi",
                                      responsible,
                                      'config.warehouse.services.order_warehouse_operation')

    def driver_send_barcode_create(self, cancelled_order_id, new_order_id, match_order_products):

        cancelled_order = Order.objects.filter(id=cancelled_order_id, cancelled_status="1", status=5).select_for_update().first()
        new_order = Order.objects.filter(id=new_order_id, status=1).select_for_update().first()
        if not cancelled_order or not new_order:
            return False

        Order.objects.filter(id=cancelled_order_id).update(is_there_product=new_order, cancelled_status='2')
        # cancelled_order.is_there_product = new_order
        # cancelled_order.cancelled_status = 2
        # cancelled_order.save()

        new_order.is_send_barcode = True
        new_order.status = 2
        new_order.is_there_previous_order = cancelled_order
        new_order.cancelled_status = 1
        new_order.driver = cancelled_order.driver
        new_order.driver_fee = cancelled_order.driver_fee
        new_order.driver_fee_standard = cancelled_order.driver_fee_standard
        new_order.save()

        driver = cancelled_order.driver
        # belgilangan orderlarni
        warehouse = WareHouse.objects.get(id=1)
        warehouse_operation_services = WarehouseOperationManager()

        warehouse_operation_item_details_services = WarehouseOperationItemDetailsManager()
        warehouse_operation_item_services = WarehouseOperationItemManager()

        warehouse_operation = warehouse_operation_services.warehouse_operation_driver_send_barcode_get_or_create(
            warehouse, driver, driver)

        WarehouseOperationAndOrderRelations.objects.create(action=3, warehouse_operation=warehouse_operation,
                                                           order=new_order)


        for new_match_order_product_id, cancelled_order_product_id in match_order_products.items():
            cancelled_order_product = OrderProduct.objects.get(order=cancelled_order, id=cancelled_order_product_id)
            new_order_product = OrderProduct.objects.get(order=new_order, id=new_match_order_product_id)

            if cancelled_order_product.product_type == '2':
                cancelled_collection_order_products = OrderProduct.objects.filter(
                    main_order_product=cancelled_order_product)
                for cancelled_collection_order_product in cancelled_collection_order_products:

                    amount = cancelled_order_product.total_quantity
                    product = cancelled_collection_order_product.product
                    product_variable = cancelled_collection_order_product.product_variable
                    new_collection_order_product = OrderProduct.objects.get(main_order_product=new_order_product,
                                                                            product=product)

                    warehouse_operation_item = warehouse_operation_item_services.operation_item_create(
                        warehouse_operation,
                        product,
                        product_variable,
                        None, amount)
                    leave_checked_amount = amount
                    cancelled_order_product_warehouse_operation_item_details = WarehouseOperationItemDetails.objects.filter(
                        order_product=cancelled_collection_order_product,
                        leave_amount__gt=0)
                    # forda aylanib bundagi mahsulotlarni yangiga belgilab chiqamiz
                    for warehouse_operation_item_detail in cancelled_order_product_warehouse_operation_item_details:
                        # yangi item detauks ochish
                        warehouse_operation_item_details_services.operation_item_details_create_send_barcode(
                            warehouse_operation_item_detail,
                            warehouse_operation,
                            warehouse_operation_item,
                            new_collection_order_product
                        )
                        leave_checked_amount -= warehouse_operation_item_detail.leave_amount
                        warehouse_operation_item_detail.leave_amount = 0
                        warehouse_operation_item_detail.save()

                    cancelled_collection_order_product.save()
                    new_collection_order_product.save()

            if int(cancelled_order_product.product_type) in [3, 1]:
                amount = cancelled_order_product.total_quantity
                if cancelled_order_product == '3':
                    amount = cancelled_order_product.main_order_product.total_quantity
                product = cancelled_order_product.product
                product_variable = cancelled_order_product.product_variable
                warehouse_operation_item = warehouse_operation_item_services.operation_item_create(warehouse_operation,
                                                                                                   product,
                                                                                                   product_variable,
                                                                                                   None, amount)
                leave_checked_amount = amount
                cancelled_order_product_warehouse_operation_item_details = WarehouseOperationItemDetails.objects.filter(
                    order_product=cancelled_order_product,
                    leave_amount__gt=0)
                # forda aylanib bundagi mahsulotlarni yangiga belgilab chiqamiz
                for warehouse_operation_item_detail in cancelled_order_product_warehouse_operation_item_details:
                    # yangi item detauks ochish
                    warehouse_operation_item_details_services.operation_item_details_create_send_barcode(
                        warehouse_operation_item_detail,
                        warehouse_operation,
                        warehouse_operation_item,
                        new_order_product
                    )
                    leave_checked_amount -= warehouse_operation_item_detail.leave_amount
                    warehouse_operation_item_detail.leave_amount = 0
                    warehouse_operation_item_detail.save()
            new_order_product.driver = cancelled_order_product.driver
            new_order_product.save()
            cancelled_order_product.save()
        return True

    def driver_send_barcode_accept(self, warehouse_operation):
        orders_id = self._warehouse_operation_and_order_relations_get_orders_id(warehouse_operation)
        Order.objects.filter(id__in=orders_id).update(status=3, is_site_change=False,
                                                      driver_shipping_start_date=datetime.datetime.today().strftime(("%Y-%m-%d")),
                                                      cancelled_status=1)


    def driver_send_barcode_cancel(self, warehouse_operation):
        orders_id = self._warehouse_operation_and_order_relations_get_orders_id(warehouse_operation)

        new_orders = Order.objects.filter(id__in=orders_id)

        for new_order in new_orders:
            cancelled_order = new_order.is_there_previous_order
            Order.objects.filter(id=cancelled_order.id).update(is_there_product=None, cancelled_status=1)

            new_order.is_send_barcode = False
            new_order.status = 1
            new_order.is_there_previous_order = None
            new_order.cancelled_status = 0
            new_order.driver = None
            new_order.save()

            new_order_product = OrderProduct.objects.filter(order=new_order).update(driver=None)



    def driver_send_product(self,driver, order, responsible):
        order.driver = driver
        order.status = 2
        order.updated_at = datetime.datetime.now()
        order.save()
        order.update_driver_fee()

        save_order_status_history(order, 2, "Buyurtma hodim tarafidan mahsulot yuborildiga olindi",
                                  responsible,
                                  'config.warehouse.services.order_warehouse_operation')

        OrderProduct.objects.filter(order=order).update(driver=driver)
        from_warehouse = WareHouse.objects.get(id=1)

        warehouse_operation_service = warehouse_operation_manager.WarehouseOperationManager()
        warehouse_operation_item_details_services = WarehouseOperationItemDetailsManager()
        warehouse_operation_item_services = WarehouseOperationItemManager()
        warehouse_stock_manager_service = WarehouseStockManager()

        warehouse_operation = warehouse_operation_service.warehouse_operation_driver_send_product_get_or_create(
            from_warehouse, driver, responsible)

        WarehouseOperationAndOrderRelations.objects.create(action=1, warehouse_operation=warehouse_operation, order=order)
        order_products = OrderProduct.objects.filter(product_type__in=[1, 3], order=order)

        for order_product in order_products:
            amount = order_product.total_quantity
            if order_product.product_type == '3':
                amount = order_product.main_order_product.total_quantity

            product = order_product.product
            product_variable = order_product.product_variable

            warehouse_stock = WareHouseStock.objects.select_for_update().filter(warehouse=from_warehouse,
                                                                                    product=product,
                                                                                    product_variable=product_variable,
                                                                                    amount__gte=amount).first()
            if not warehouse_stock: raise InsufficientStockError(product.name)
            warehouse_stock.amount -= amount
            warehouse_stock.save()
            warehouse_stock_manager_service.warehouse_stock_history_add(warehouse_stock, amount, responsible,
                                                                            "OrderProduct", order_product.id)

            warehouse_operation_item = warehouse_operation_item_services.operation_item_create(warehouse_operation, product, product_variable, warehouse_stock, amount)

            leave_checked_amount = amount
            for item_details in warehouse_stock.get_warehouse_operation_item_details_queryset:
                    if leave_checked_amount > 0:
                        current_leave_amount = min(item_details.leave_amount, leave_checked_amount)
                        input_price = item_details.input_price
                        warehouse_operation_item_details_services.operation_item_details_create(
                            item_details.warehouse_operation, item_details.warehouse_operation_item,
                            item_details, warehouse_stock, warehouse_operation, warehouse_operation_item, product,
                            product_variable, input_price, current_leave_amount, current_leave_amount,
                            input_price, order_product
                        )
                        item_details.leave_amount -= current_leave_amount
                        leave_checked_amount -= current_leave_amount
                        item_details.save()
        


    def driver_return_product_from_driver(self, driver, order, responsible):
        Order.objects.filter(id=order.id).update(status=5, cancelled_status=3)

        save_order_status_history(order, 5, "Buyurtmani mahsuloti hodim tarafidan qaytarib olindi",
                                  responsible,
                                  'config.warehouse.services.order_warehouse_operation')

        # ------operation get or create qilamiz
        to_warehouse = WareHouse.objects.get(id=1)
        warehouse_operation_service = WarehouseOperationManager()
        warehouse_operation_item_details_services = WarehouseOperationItemDetailsManager()
        warehouse_operation_item_services = WarehouseOperationItemManager()
        warehouse_operation = warehouse_operation_service.warehouse_operation_driver_return_product_get_or_create(
            to_warehouse, driver, responsible)
        WarehouseOperationAndOrderRelations.objects.create(action=2, warehouse_operation=warehouse_operation,
                                                           order=order)


        order_products = OrderProduct.objects.filter(product_type__in=[1, 3], order=order)
        # buni aylanib harbir temni detailslariga mos boshqalarini yaratish kerak
        for order_product in order_products:
            amount = order_product.ordered_amount
            if order_product.product_type == '3':
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
                # bu xato shu ki agar order product admounti bilan warehouse operation details da confilict chiqsa soni bir biriga to'g'ri kelmaa
            # order_product.amount = 0
            # order_product.status = "5"
            # order_product.save()
            order_product.save()
        return True


    def driver_return_product_cancel(self, warehouse_operation, responsible=None):
        # hamma qaytarib olinganlarni joyiga qaytarish kerak
        orders_id = self._warehouse_operation_and_order_relations_get_orders_id(warehouse_operation)
        Order.objects.filter(id__in=orders_id).update(status=5, cancelled_status="1")

        orders = Order.objects.filter(id__in=orders_id)
        for order in orders:
            save_order_status_history(order, 5, "Mahsulotni qaytarib olish amaliyoti bekor qilindi",
                                      responsible,
                                      'config.warehouse.services.order_warehouse_operation')

    # def driver_send_product(self,driver, order, responsible):
    #
    #     order.status = 2
    #     order.is_site_change = False
    #     order.save()
    #
    #     from_warehouse = WareHouse.objects.get(id=1)
    #
    #     warehouse_operation_service = warehouse_operation_manager.WarehouseOperationManager()
    #     warehouse_operation_item_details_services = WarehouseOperationItemDetailsManager()
    #     warehouse_operation_item_services = WarehouseOperationItemManager()
    #     warehouse_stock_manager_service = WarehouseStockManager()
    #
    #     warehouse_operation = warehouse_operation_service.warehouse_operation_driver_send_product_get_or_create(
    #         from_warehouse, driver, responsible)
    #
    #     WarehouseOperationAndOrderRelations.objects.create(action=1, warehouse_operation=warehouse_operation, order=order)
    #     order_products = OrderProduct.objects.filter(order=order)
    #     for order_product in order_products:
    #         amount = order_product.ordered_amount
    #         product_type = order_product.type
    #         product = order_product.product
    #         product_variable = order_product.product_variable
    #
    #         if product_type == "1":  # donali
    #             warehouse_stock = WareHouseStock.objects.select_for_update().filter(warehouse=from_warehouse,
    #                                                                                 product=product,
    #                                                                                 product_variable=product_variable,
    #                                                                                 amount__gte=amount).first()
    #             if not warehouse_stock: raise InsufficientStockError(product.name)
    #
    #             warehouse_stock.amount -= amount
    #             warehouse_stock.save()
    #             warehouse_stock_manager_service.warehouse_stock_history_add(warehouse_stock, amount, responsible,
    #                                                                         "OrderProduct", order_product.id)
    #
    #             warehouse_operation_item = warehouse_operation_item_services.operation_item_create(warehouse_operation, product, product_variable, warehouse_stock, amount)
    #
    #             leave_checked_amount = amount
    #             for item_details in warehouse_stock.get_warehouse_operation_item_details_queryset:
    #                 if leave_checked_amount > 0:
    #                     current_leave_amount = min(item_details.leave_amount, leave_checked_amount)
    #                     input_price = item_details.input_price
    #                     warehouse_operation_item_details_services.operation_item_details_create(
    #                         item_details.warehouse_operation, item_details.warehouse_operation_item,
    #                         item_details, warehouse_stock, warehouse_operation, warehouse_operation_item, product,
    #                         product_variable, input_price, current_leave_amount, current_leave_amount,
    #                         input_price, order_product
    #                     )
    #                     item_details.leave_amount -= current_leave_amount
    #                     leave_checked_amount -= current_leave_amount
    #                     item_details.save()
    #
    #
    #         elif product_type == "2":  # to'plam
    #             collection_item = OrderProductCollectionItem.objects.filter(order_product=order_product)
    #             for c in collection_item:
    #                 warehouse_stock = WareHouseStock.objects.select_for_update().filter(warehouse=from_warehouse,
    #                                                                                     product=c.product,
    #                                                                                     product_variable=c.product_variable,
    #                                                                                     amount__gte=amount).first()
    #                 if not warehouse_stock: raise InsufficientStockError(c.product.name)
    #                 warehouse_stock.amount -= amount
    #                 warehouse_stock.save()
    #                 warehouse_stock_manager_service.warehouse_stock_history_add(warehouse_stock, amount, responsible,
    #                                                                             "OrderProduct", order_product.id)
    #                 warehouse_operation_item = warehouse_operation_item_services.operation_item_create(
    #                     warehouse_operation, c.product, c.product_variable, warehouse_stock, amount)
    #                 leave_checked_amount = amount
    #                 for item_details in warehouse_stock.get_warehouse_operation_item_details_queryset:
    #                     if leave_checked_amount > 0:
    #                         current_leave_amount = min(item_details.leave_amount, leave_checked_amount)
    #                         input_price = item_details.input_price
    #                         warehouse_operation_item_details_services.operation_item_details_create(
    #                             item_details.warehouse_operation, item_details.warehouse_operation_item,
    #                             item_details, warehouse_stock, warehouse_operation, warehouse_operation_item, c.product,
    #                             c.product_variable, input_price, current_leave_amount, current_leave_amount,
    #                             input_price, order_product
    #                         )
    #                         item_details.leave_amount -= current_leave_amount
    #                         leave_checked_amount -= current_leave_amount
    #                         item_details.save()