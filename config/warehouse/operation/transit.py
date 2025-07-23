from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from warehouse.models import WareHouse, WareHouseStock, WarehouseOperation, WarehouseOperationItem, \
    WareHouseStockHistory, WarehouseOperationItemDetails
from config.warehouse.permission import warehouse_permission_check
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
import datetime
import json
from config.warehouse.services.warehouse_operation_manager import WarehouseOperationManager
from config.warehouse.services.warehouse_stock_manager import WarehouseStockManager
from config.warehouse.services.warehouse_operation_item_details_manager import WarehouseOperationItemDetailsManager



def add_interest(principal, rate=5):
    if principal is None or principal == 0:
        return 0
    interest = principal * rate / 100
    total_amount = principal + interest
    return total_amount


@login_required(login_url='/login')
def warehouse_operation_transit_product(request, warehouse_id):
    warehouse = get_object_or_404(WareHouse, id=warehouse_id)
    if warehouse_permission_check('warehouse_operation_transit_product',request.user, warehouse_id) is False:
        messages.error(request, "Sizga kirish uchun ruxsat yo'q")
        return redirect('home')
    if request.method == "POST":
        try:
            with transaction.atomic():
                r = request.POST
                products = json.loads(request.POST["products"])
                user = request.user
                to_warehouse = WareHouse.objects.get(id=r['warehouse'])
                operation_services = WarehouseOperationManager()
                operation = operation_services.operation_transit_create(warehouse, r['desc'], to_warehouse, user, products)
                for i in products:
                    warehouse_stock_services = WarehouseStockManager()

                    warehouse_stock, reduce_amount = warehouse_stock_services.warehouse_stock_amount_reduce(i['id'], int(i['checked_amount']))
                    new_operation_item = WarehouseOperationItem.objects.create(warehouse_operation=operation,
                                                                     product_id=i['product_id'],
                                                                     product_variable_id=i['product_variable_id'],
                                                                     amount=reduce_amount,
                                                                     input_price=warehouse_stock.input_price
                                                                     )

                    warehouse_stock_services.warehouse_stock_history_add(warehouse_stock, reduce_amount, user, "WarehouseOperationItem", new_operation_item.id)
                    warehouse_operation_item_details_services = WarehouseOperationItemDetailsManager()
                    leave_checked_amount = reduce_amount
                    for i in warehouse_stock.get_warehouse_operation_item_details_queryset:
                        if leave_checked_amount > 0:
                            current_leave_amount = min(i.leave_amount, leave_checked_amount)
                            input_price = i.input_price
                            if warehouse_id == 3 and to_warehouse.id == 1:
                                input_price=add_interest(i.input_price)

                            warehouse_operation_item_details_services.operation_item_details_create(
                                i.warehouse_operation, i.warehouse_operation_item,
                                i, warehouse_stock, operation, new_operation_item, i.product,
                                i.product_variable, input_price, current_leave_amount, current_leave_amount,
                                i.input_price
                            )
                            i.leave_amount -= current_leave_amount
                            leave_checked_amount -= current_leave_amount
                            i.save()
                messages.success(request, f"Ma'lumotlar saqlandi")
                return redirect('warehouse_list')
        except IntegrityError as e:
            messages.error(request, f"Sizda hatolik {e}")
            return redirect('warehouse_list')

    warehouse_list = WareHouse.objects.filter(id__in=[1,2,3]).exclude(id=warehouse_id)
    warehouse_stock = json.dumps([dict(a, checked_price=0, checked_amount=0, is_check=0) for a in WareHouseStock.objects.filter(warehouse=warehouse).values("id","product_id", "product__name",
                                                                               'product_variable_id', 'product_variable__measure_item__name',
                                                                               'product_variable__color__name',
                                                                               'amount', 'selling_price', 'input_price'
                                                                               )])
    return render(request, 'warehouse/operation/transit.html', {"warehouse_list":warehouse_list, 'warehouse':warehouse, 'warehouse_stock':warehouse_stock})


