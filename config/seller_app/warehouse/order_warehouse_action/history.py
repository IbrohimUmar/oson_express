from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from services.seller.get_seller import get_seller
from warehouse.models import WareHouse, WarehouseOperation, OrderWarehouseAction
from django.core.paginator import Paginator
from config.seller_app.warehouse.permission import warehouse_permission_required


@login_required(login_url='/login')
@warehouse_permission_required('order_warehouse_action_history')
def seller_app_warehouse_order_warehouse_action_history(request, warehouse_id):
    seller = get_seller(request.user)
    warehouse = get_object_or_404(WareHouse, id=warehouse_id, responsible=seller)
    order_warehouse_action = OrderWarehouseAction.objects.filter(warehouse=warehouse)
    warehouse.perms = warehouse.get_user_permission(request.user)


    filter_query = request.GET.get("filter", None)
    if filter_query:
        order_warehouse_action = order_warehouse_action.filter(Q(order__id__icontains=filter_query) | Q(order__barcode__icontains=filter_query))


    type = request.GET.get("type", 'None')
    if type != 'None':
        order_warehouse_action = order_warehouse_action.filter(type=type)

    paginator = Paginator(order_warehouse_action, 10)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/warehouse/order_warehouse_action/history.html', {
                                                                            "page_obj": queryset,
                                                                            "count": order_warehouse_action.count(),
                                                                             'warehouse' :warehouse,
                                                                             "operation_types" :WarehouseOperation.action_type})
