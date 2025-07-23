from django.db import transaction

from warehouse.models import WarehouseOperationItemDetails


class WarehouseOperationItemDetailsManager:
    def operation_item_details_rollback(self, operation):
            operation_item_details_list = WarehouseOperationItemDetails.objects.select_for_update().filter(warehouse_operation=operation, leave_amount__gt=0)
            for o in operation_item_details_list:
                from_details = WarehouseOperationItemDetails.objects.select_for_update().filter(id=o.from_warehouse_operation_item_details.id).first()
                from_details.leave_amount += o.leave_amount
                o.leave_amount = 0
                o.save()
                from_details.save()


    def operation_item_details_create(self, from_warehouse, from_warehouse_item, from_warehouse_item_details,
                                      from_warehouse_stock, operation, operation_item, product, product_variable, input_price, amount, leave_amount, from_warehouse_input_price=0, order_product=None):
        result = WarehouseOperationItemDetails.objects.create(
            from_warehouse_operation=from_warehouse,
            from_warehouse_operation_item=from_warehouse_item,
            from_warehouse_operation_item_details=from_warehouse_item_details,
            from_warehouse_stock=from_warehouse_stock,
            from_warehouse_input_price=from_warehouse_input_price,
            warehouse_operation=operation,
            warehouse_operation_item=operation_item,
            product=product,
            product_variable=product_variable,
            input_price=input_price,
            amount=amount,
            leave_amount=leave_amount,
                order_product=order_product

        )
        return result


    def operation_item_details_create_return_product(self, from_warehouse_operation_item_details,
                                                     warehouse_operation, warehouse_operation_item):
        result = WarehouseOperationItemDetails.objects.create(
                from_warehouse_operation=from_warehouse_operation_item_details.warehouse_operation,
                from_warehouse_operation_item=from_warehouse_operation_item_details.warehouse_operation_item,
                from_warehouse_operation_item_details=from_warehouse_operation_item_details,
                from_warehouse_stock=from_warehouse_operation_item_details.warehouse_stock,
                from_order_product=from_warehouse_operation_item_details.order_product,
                from_warehouse_input_price=from_warehouse_operation_item_details.input_price,

                warehouse_operation=warehouse_operation,
                warehouse_operation_item=warehouse_operation_item,

                warehouse_stock=None,
                product=from_warehouse_operation_item_details.product,
                product_variable=from_warehouse_operation_item_details.product_variable,

                input_price=from_warehouse_operation_item_details.input_price,
                amount=from_warehouse_operation_item_details.leave_amount,
                leave_amount=from_warehouse_operation_item_details.leave_amount,
                                                         )
        # WarehouseOperationItemDetails.objects.create(
        #     from_warehouse_operation=warehouse_operation_item_detail.warehouse_operation,
        #     from_warehouse_operation_item=warehouse_operation_item_detail.warehouse_operation_item,
        #     from_warehouse_operation_item_details=warehouse_operation_item_detail,
        #     from_warehouse_stock=warehouse_operation_item_detail.warehouse_stock,
        #     from_order_product=order_product,
        #     from_warehouse_input_price=warehouse_operation_item_detail.input_price,
        #
        #     warehouse_operation=warehouse_operation,
        #     warehouse_operation_item=warehouse_operation_item,
        #
        #     warehouse_stock=None,
        #     product=product,
        #     product_variable=product_variable,
        #
        #     input_price=warehouse_operation_item_detail.input_price,
        #     amount=warehouse_operation_item_detail.leave_amount,
        #     leave_amount=warehouse_operation_item_detail.leave_amount,
        #                                              )
        return result



    def operation_item_details_create_send_barcode(self, from_warehouse_operation_item_details,
                                                     warehouse_operation, warehouse_operation_item, to_order_product):
        result = WarehouseOperationItemDetails.objects.create(
                from_warehouse_operation=from_warehouse_operation_item_details.warehouse_operation,
                from_warehouse_operation_item=from_warehouse_operation_item_details.warehouse_operation_item,
                from_warehouse_operation_item_details=from_warehouse_operation_item_details,
                from_warehouse_stock=from_warehouse_operation_item_details.warehouse_stock,
                from_order_product=from_warehouse_operation_item_details.order_product,
                from_warehouse_input_price=from_warehouse_operation_item_details.input_price,

                warehouse_operation=warehouse_operation,
                warehouse_operation_item=warehouse_operation_item,
                order_product=to_order_product,

                warehouse_stock=None,
                product=from_warehouse_operation_item_details.product,
                product_variable=from_warehouse_operation_item_details.product_variable,

                input_price=from_warehouse_operation_item_details.input_price,
                amount=from_warehouse_operation_item_details.leave_amount,
                leave_amount=from_warehouse_operation_item_details.leave_amount,
                                                         )
        return result
