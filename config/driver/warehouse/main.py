from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from user.models import User
from warehouse.models import WarehouseOperation


@login_required(login_url='/login')
@permission_required('admin.driver_warehouse', login_url="/home")
def driver_warehouse(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    return render(request, 'driver/warehouse/main.html', {"d":driver})



