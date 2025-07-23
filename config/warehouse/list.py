from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render

from warehouse.models import WarehouseOperation, WareHouse

@login_required(login_url='/login')
@permission_required('admin.warehouse_list', login_url="/home")
def warehouse_list(request):
    warehouse = list(WareHouse.objects.filter(id__in=[1, 2 ,3]).values("id", "responsible__first_name", "responsible__last_name"))
    for w in warehouse:
        w['operation_count'] = WarehouseOperation.objects.filter(Q(from_warehouse_id=w['id'], from_warehouse_status='1')|Q(from_warehouse_status='2',to_warehouse_id=w["id"], to_warehouse_status='1')).count()
    return render(request, 'warehouse/list.html', {"warehouse":warehouse})