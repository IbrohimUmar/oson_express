import datetime

from config.seller_app.warehouse.services.warehouse_operation_item_details_manager import WarehouseOperationItemDetailsManager
from config.seller_app.warehouse.services.warehouse_operation_item_manager import WarehouseOperationItemManager
from user.models import User
from warehouse.models import WarehouseOperation
# , WarehouseOperationItem, WarehouseOperationItemDetails)


class WarehouseOperationManager:
    @property
    def get_warehouse_operation_item_manager(self):
        result = WarehouseOperationItemManager()
        return result
    @property
    def get_warehouse_operation_item_details_manager(self):
        result = WarehouseOperationItemDetailsManager()
        return result


    def _get_user_or_none(self, id):
        print(id)
        if id:
            return User.objects.filter(id=id).first()
        return None


    def operation_transit_create(self, from_warehouse, desc, to_warehouse, responsible, product_json):
        operation = WarehouseOperation.objects.create(
            action="1", from_warehouse=from_warehouse,
            from_warehouse_responsible=from_warehouse.responsible,
            from_warehouse_desc=desc,
            from_warehouse_status="1",

            to_warehouse=to_warehouse,
            to_warehouse_responsible=to_warehouse.responsible,
            to_warehouse_status="1",

            responsible=responsible,
            creating_user=responsible
        )
        return operation



    def warehouse_operation_driver_send_product_get_or_create(self,from_warehouse, driver, responsible):
        warehouse_operation = WarehouseOperation.objects.filter(action='3',from_warehouse_status="1", to_warehouse_responsible=driver, to_warehouse_status="1").last()
        if not warehouse_operation:
            warehouse_operation = WarehouseOperation.objects.create(action='3',from_warehouse=from_warehouse, from_warehouse_responsible=from_warehouse.responsible,
            from_warehouse_status="1", to_warehouse_responsible=driver, to_warehouse_status="1",responsible=responsible,
                                                                    creating_user=responsible)
        return warehouse_operation


    def warehouse_operation_driver_return_product_get_or_create(self,to_warehouse, driver, responsible):
        warehouse_operation = WarehouseOperation.objects.filter(action='4', from_warehouse_status="1", from_warehouse_responsible=driver, to_warehouse_status="1").last()
        if not warehouse_operation:
            warehouse_operation = WarehouseOperation.objects.create(action='4',to_warehouse=to_warehouse, from_warehouse_responsible=driver,
            from_warehouse_status="1", to_warehouse_responsible=to_warehouse.responsible,
                                                                    to_warehouse_status="1",responsible=responsible,
                                                                    creating_user=responsible)
        return warehouse_operation


    def warehouse_operation_driver_return_product_cancel(self, operation, responsible, cancel_note):
        operation.from_warehouse_status = "3"
        operation.from_warehouse_status_changed_user = responsible
        operation.from_warehouse_confirm_date = datetime.datetime.now()
        operation.responsible = responsible
        operation.from_warehouse_desc = cancel_note
        operation.save()
        self.get_warehouse_operation_item_details_manager.operation_item_details_rollback(operation)
        return operation


    def warehouse_operation_driver_send_barcode_get_or_create(self,to_warehouse, driver, responsible):
        warehouse_operation = WarehouseOperation.objects.filter(action='5', from_warehouse_status="1", from_warehouse_responsible=driver, to_warehouse_status="1").last()
        if not warehouse_operation:
            warehouse_operation = WarehouseOperation.objects.create(action='5', to_warehouse_responsible=driver, from_warehouse_responsible=driver,
            from_warehouse_status="1",
                                                                    to_warehouse_status="1",responsible=responsible,
                                                                    creating_user=responsible)
        return warehouse_operation




    def operation_partner_product_in_warehouse_create(self, warehouse, desc, responsible, product_json, partner=None):
        operation = WarehouseOperation.objects.create(
            action=2,
            from_warehouse_responsible=self._get_user_or_none(partner),
            from_warehouse_status_changed_user=responsible,
            from_warehouse_desc=desc,
            from_warehouse_status="2",
            from_warehouse_confirm_date=datetime.datetime.now(),
            responsible=responsible,
            creating_user=responsible,
            to_warehouse=warehouse,
            to_warehouse_responsible=warehouse.responsible,
        )
        operation_items = [
            WarehouseOperationItem(
                warehouse_operation=operation,
                product_id=i['product_id'],
                product_variable_id=i['id'],
                input_price=i['price'],
                amount=int(i['amount']),
            )
            for i in product_json
        ]
        WarehouseOperationItem.objects.bulk_create(operation_items)
        op_items = WarehouseOperationItem.objects.filter(warehouse_operation=operation)
        operation_items_details = []
        for i in op_items:
            operation_items_details.append(
                WarehouseOperationItemDetails(
                    warehouse_operation=operation,
                    warehouse_operation_item=i,
                    product=i.product,
                    product_variable=i.product_variable,
                    input_price=i.input_price,
                    amount=i.amount,
                    leave_amount=i.amount
                )
            )
        WarehouseOperationItemDetails.objects.bulk_create(operation_items_details)
        return operation



    def operation_accept_to_driver_warehouse(self, operation, responsible):
        operation.to_warehouse_status = "2"
        operation.to_warehouse_status_changed_user = responsible
        operation.to_warehouse_confirm_date = datetime.datetime.now()
        operation.responsible = responsible
        operation.save()
        return operation
        
    def operation_to_warehouse_accept(self, operation, responsible):
        operation.to_warehouse_status = "2"
        operation.to_warehouse_status_changed_user = responsible
        operation.to_warehouse_confirm_date = datetime.datetime.now()
        operation.responsible = responsible
        operation.save()

        self.get_warehouse_operation_item_manager.operation_item_add_warehouse_stock(operation, operation.to_warehouse, responsible)
        return operation

    def operation_to_warehouse_cancel(self, operation, responsible, cancel_note):
        operation.to_warehouse_status = "3"
        operation.to_warehouse_status_changed_user = responsible
        operation.to_warehouse_confirm_date = datetime.datetime.now()
        operation.responsible = responsible
        operation.to_warehouse_desc = cancel_note
        operation.save()
        return operation

    def operation_from_warehouse_accept(self, operation, responsible):
        operation.from_warehouse_status = "2"
        operation.from_warehouse_status_changed_user = responsible
        operation.from_warehouse_confirm_date = datetime.datetime.now()
        operation.responsible = responsible
        operation.save()
        return operation

    def operation_from_warehouse_cancel(self, operation, responsible, cancel_note):
        operation.from_warehouse_status = "3"
        operation.from_warehouse_status_changed_user = responsible
        operation.from_warehouse_confirm_date = datetime.datetime.now()
        operation.responsible = responsible
        operation.from_warehouse_desc = cancel_note
        operation.save()
        self.get_warehouse_operation_item_manager.operation_item_add_warehouse_stock(operation, operation.from_warehouse, responsible)
        self.get_warehouse_operation_item_details_manager.operation_item_details_rollback(operation)
        return operation
