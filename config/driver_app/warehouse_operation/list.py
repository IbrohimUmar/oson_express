from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from config.driver_app.permission import is_driver
from warehouse.models import WarehouseOperation


@is_driver
def driver_app_warehouse_operation_list(request):
    warehouse_operation = WarehouseOperation.objects.filter(action='3', to_warehouse_responsible=request.user, to_warehouse_status='2').order_by('-id')
    paginator = Paginator(warehouse_operation, 10)
    page_number = request.GET.get('page', 1)
    queryset = paginator.get_page(page_number)
    return render(request, 'driver_app/warehouse_operation/list.html',{'page_obj':queryset, 'count':warehouse_operation.count()})