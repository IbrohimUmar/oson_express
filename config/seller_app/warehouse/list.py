from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render

from warehouse.models import WarehouseOperation, WareHouse, WarehousePermission


@login_required(login_url='/login')
@permission_required('admin.seller_app_warehouse_list', login_url="/home")
def seller_app_warehouse_list(request):
    '''
    seller bo'lsa
    yoki dostup berilgan bo'lsa
    '''
    warehouse_permission = WarehousePermission.objects.filter(user=request.user)
    warehouses_id = list(warehouse_permission.filter(has_view=True).values_list('warehouse_id', flat=True))
    warehouses = WareHouse.objects.filter(id__in=warehouses_id)
    for warehouse in warehouses:
        warehouse.perms = warehouse.get_user_permission(request.user)
    return render(request, 'seller_app/warehouse/list.html', {"warehouses":warehouses})