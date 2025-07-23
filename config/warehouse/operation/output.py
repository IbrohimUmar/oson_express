from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404

from warehouse.models import WareHouse


@login_required(login_url='/login')
@permission_required('admin.warehouse_operation_product_output', login_url="/home")
def warehouse_operation_output_product(request, warehouse_id):
    warehouse = get_object_or_404(WareHouse, id=warehouse_id)
    return render(request, 'warehouse/list.html')
