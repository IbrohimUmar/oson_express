import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404

from order.models import Order, OrderProduct
from warehouse.models import WareHouse, WarehouseOperationAndOrderRelations
from store.models import ProductVariable
import json
from user.models import User
from config.warehouse.services.warehouse_operation_manager import WarehouseOperationManager
from django.db import transaction, IntegrityError
from config.warehouse.permission import warehouse_permission_check
from warehouse.models import WarehouseOperation, WarehouseOperationItem



@login_required(login_url='/login')
@permission_required('admin.warehouse_operation_edit', login_url="/home")
def warehouse_operation_edit(request, warehouse_id, warehouse_operation_id):
    if warehouse_permission_check('warehouse_operation_history',request.user, warehouse_id) is False:
        messages.error(request, "Sizga kirish uchun ruxsat yo'q")
        return redirect('home')
    warehouse = get_object_or_404(WareHouse, id=warehouse_id)
    warehouse_operation = get_object_or_404(WarehouseOperation, id=warehouse_operation_id, to_warehouse_status="1", action="3")
    if request.method == "POST":
        try:
            with transaction.atomic():
                r = request.POST
                warehouse_operation = get_object_or_404(WarehouseOperation, id=warehouse_operation_id,
                                                        to_warehouse_status="1", action="3")
                driver = r['driver']
                warehouse_operation = WarehouseOperation.objects.filter(id=warehouse_operation_id).update(to_warehouse_responsible_id=driver)
                warehouse_relations_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=warehouse_operation_id).values_list("order_id", flat=True))
                Order.objects.filter(id__in=warehouse_relations_id).update(driver_id=driver)
                OrderProduct.objects.filter(order_id__in=warehouse_relations_id).update(driver_id=driver)
            messages.success(request, f"O'zgartirildi")
            return redirect('warehouse_operation_edit', warehouse_id, warehouse_operation_id)
        except IntegrityError as e:
            messages.error(request, f"Sizda hatolik {e}")
            return redirect('warehouse_list')
    drivers = User.objects.filter(is_active=True, type='2')
    return render(request, 'warehouse/operation/edit.html', {'warehouse':warehouse,"i":warehouse_operation, "drivers":drivers})
