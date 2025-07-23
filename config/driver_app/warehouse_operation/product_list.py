from asgiref.sync import async_to_sync
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect

from config.driver_app.permission import is_driver
from warehouse.models import WarehouseOperation, WarehouseOperationItemDetails


@is_driver
def driver_app_warehouse_operation_product_list(request, warehouse_operation_id):
    warehouse_operation = get_object_or_404(WarehouseOperation, id=warehouse_operation_id)
    driver = request.user
    if warehouse_operation.from_warehouse_responsible == driver or warehouse_operation.to_warehouse_responsible == driver:
        warehouse_item_details = WarehouseOperationItemDetails.objects.filter(warehouse_operation=warehouse_operation).values("product_variable_id", 'product_variable__product__name', 'product_variable__color__name', 'product_variable__measure_item__name').annotate(
            count=Sum("amount")
        )
        print(warehouse_item_details)
        return render(request, 'driver_app/warehouse_operation/product_list.html', {"warehouse_operation":warehouse_operation, 'warehouse_item_details':warehouse_item_details})

    messages.success(request, 'Bu operatsiya sizga tegishli emas')
    return redirect('driver_app_warehouse_operation_history')
