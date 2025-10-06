# from warehouse.models import WarehouseOperationItem, WarehouseOperationItemDetails



class WarehouseOperationItemManager:
    def operation_item_add_warehouse_stock(self, operation, warehouse, responsible):
        pass
        # operation_item = WarehouseOperationItem.objects.select_for_update().filter(warehouse_operation=operation)
        # stock_manager = WarehouseStockManager()
        # for o in operation_item:
        #     stock = stock_manager.warehouse_stock_add(warehouse.id, o.product.id, o.product_variable.id, o.amount, o.input_price)
        #     o.warehouse_stock = stock
        #     WarehouseOperationItemDetails.objects.filter(warehouse_operation_item=o).update(warehouse_stock=stock)
        #     o.save()
        #     stock_manager.warehouse_stock_history_add(stock, o.amount, responsible, "WarehouseOperationItem", o.id)




    def operation_item_create(self, warehouse_operation, product, product_variable,warehouse_stock, amount, input_price=0, selling_price=0):
        # warehouse_operation_item = WarehouseOperationItem.objects.create(
        #     warehouse_operation=warehouse_operation,
        #     product=product,
        #     product_variable=product_variable,
        #     input_price=input_price,
        #     warehouse_stock=warehouse_stock,
        #     selling_price=selling_price,
        #     amount=amount
        # )
        # return warehouse_operation_item
        pass
