from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from config.driver_app.permission import is_driver
from store.models import Product
from postage.models import Postage

from order.models import Order
@is_driver
@async_to_sync
async def driver_app_warehouse_operation_order_list(request, warehouse_operation_id):
        warehouse_operation = get_object_or_404(Postage, id=warehouse_operation_id)
        district = request.user.allow_districts.all()
        return render(request, 'driver_app/warehouse_operation/order_list.html',
                    {
                        'district': district,
                        'warehouse_operation': warehouse_operation
                    })

