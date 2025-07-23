from warehouse.models import WareHouseStock, WareHouseStockHistory
import datetime

class WarehouseStockManager:

    def warehouse_stock_amount_reduce(self, stock_id, reduce_amount):
        stock = WareHouseStock.objects.select_for_update().get(id=stock_id)
        if reduce_amount > stock.amount:

            stock.attachment_amount = 0
            reduce_amount = stock.amount
            stock.amount = 0
        else:
            stock.amount -= reduce_amount
            
            
            if stock.attachment_amount is None:
                stock.attachment_amount = stock.amount
            else:
                stock.attachment_amount -= reduce_amount
            
            # stock.attachment_amount -= reduce_amount

        stock.save()
        return stock, reduce_amount


    def warehouse_stock_add(self, warehouse_id, product_id, product_variable_id, amount, input_price):
        stock = WareHouseStock.objects.select_for_update().filter(
                warehouse_id=warehouse_id,
                product_id=product_id,
                product_variable_id=product_variable_id
            ).first()
        if not stock:
            stock, created = WareHouseStock.objects.get_or_create(
                warehouse_id=warehouse_id,
                product_id=product_id,
                product_variable_id=product_variable_id,
                defaults={'amount': 0}  # Varsa oluşturma işlemi, yoksa sıfır değeriyle oluştur
            )

        # stock, create = WareHouseStock.objects.select_for_update().get_or_create(warehouse_id=warehouse_id, product_id=product_id,
        #                                                      product_variable_id=product_variable_id)
        if stock.amount:
            
            if stock.attachment_amount is None:
                stock.attachment_amount = amount
            else:
                stock.attachment_amount += amount

            stock.amount += amount
        else:
            stock.amount = amount
            stock.attachment_amount = amount
        stock.input_price = input_price
        stock.save()
        return stock

    def warehouse_stock_history_add(self, warehouse_sock, amount, responsible, model_name, model_obj_id):
        history_records = WareHouseStockHistory.objects.filter(warehouse_stock=warehouse_sock, expired_date=None)
        history_records.update(expired_date=datetime.datetime.now())
        WareHouseStockHistory.objects.create(warehouse_stock=warehouse_sock, amount=amount, model_name=model_name,
                                             obj_id=model_obj_id, responsible=responsible)
