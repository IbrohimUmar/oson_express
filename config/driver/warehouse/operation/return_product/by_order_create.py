from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render

from user.models import User


@login_required(login_url='/login')
@permission_required('admin.driver_warehouse_operation_return_product_by_order_create_scanner', login_url="/home")
def driver_warehouse_operation_return_product_by_order_create_scanner(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    return render(request, 'driver/warehouse/operation/return_product/by_order_create_scanner.html',
                  {"d": driver})