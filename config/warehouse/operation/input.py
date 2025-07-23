import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from warehouse.models import WareHouse
from store.models import ProductVariable
import json
from user.models import User
from config.warehouse.services.warehouse_operation_manager import WarehouseOperationManager
from django.db import transaction, IntegrityError
from config.warehouse.permission import warehouse_permission_check



@login_required(login_url='/login')
@permission_required('admin.warehouse_list', login_url="/home")
def warehouse_operation_input_product(request, warehouse_id):
    def get_last_input_price_product(id):
        from warehouse.models import WarehouseOperationItemDetails
        details = WarehouseOperationItemDetails.objects.filter(product_variable_id=id,
                                                               warehouse_operation__action="2").last()
        if details:
            return int(details.input_price)
        else:
            return 0
    if warehouse_permission_check('warehouse_operation_input_product',request.user, warehouse_id) is False:
        messages.error(request, "Sizga kirish uchun ruxsat yo'q")
        return redirect('home')
    warehouse = get_object_or_404(WareHouse, id=warehouse_id)
    supplier = User.objects.filter(is_active=True, type='5')
    if request.method == "POST":
        try:
            with transaction.atomic():
                products = json.loads(request.POST["products"])
                r = request.POST
                operation_manager = WarehouseOperationManager()
                operation_manager.operation_partner_product_in_warehouse_create(warehouse, r['desc'], request.user , products, {"0":None}.get(r['supplier'], r['supplier']))
            messages.success(request, f"Kirim bajarilmoqda")
            return redirect('warehouse_list')
        except IntegrityError as e:
            messages.error(request, f"Sizda hatolik {e}")
            return redirect('warehouse_list')
    product_list = json.dumps([dict(a, price=get_last_input_price_product(a['id']), amount=0, is_check=0) for a in ProductVariable.objects.all().values("id", "product_id","product__name", "measure_item__name", "color__name")])
    return render(request, 'warehouse/operation/input.html', {"product_list":product_list, "supplier":supplier})
