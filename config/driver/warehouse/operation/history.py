import os

from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from config.export_excel import export_excel_from_driver_send_product_order_details
from order.models import Order
from user.models import User

from warehouse.models import WarehouseOperation, WarehouseOperationItem, WarehouseOperationAndOrderRelations


@login_required(login_url='/login')
@permission_required('admin.driver_warehouse_operation_history', login_url="/home")
def driver_warehouse_operation_history(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    warehouse_operations = WarehouseOperation.objects.filter(Q(from_warehouse_responsible__id=driver_id)|Q(to_warehouse_responsible_id=driver_id)).order_by("-id")
    paginator = Paginator(warehouse_operations, 40)
    page_number = request.GET.get('page')
    result = paginator.get_page(page_number)
    return render(request, 'driver/warehouse/operation/history.html',{"d":driver, 'page_obj': result, 'count': warehouse_operations.count()})




@login_required(login_url='/login')
@permission_required('admin.driver_warehouse_operation_history_details_by_order', login_url="/home")
def driver_warehouse_operation_history_details_by_order(request, driver_id, warehouse_operation_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    warehouse_operations = get_object_or_404(WarehouseOperation, id=warehouse_operation_id)
    orders_id = list(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=warehouse_operation_id).values_list("order_id", flat=True))
    order = Order.objects.filter(id__in=orders_id)

    search = request.GET.get("search", None)
    if search:
        order = order.filter(
            Q(id__contains=search) | Q(customer_phone__contains=search) | Q(customer_phone2__contains=search) | Q(
                customer_name__contains=search))

    if 'excel' in request.GET:
        excel = export_excel_from_driver_send_product_order_details(order)
        static_file_path = os.path.join(excel)
        with open(static_file_path, 'rb') as file:
            file_content = file.read()
        response = HttpResponse(file_content, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="excel.xlsx"'
        return response

    paginator = Paginator(order, 40)
    page_number = request.GET.get('page')
    result = paginator.get_page(page_number)
    return render(request, 'driver/warehouse/operation/details/by_order.html',
                  {"d": driver, 'queryset': result, 'count': order.count()})



@login_required(login_url='/login')
@permission_required('admin.driver_warehouse_operation_history_details_by_product', login_url="/home")
def driver_warehouse_operation_history_details_by_product(request, driver_id, warehouse_operation_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    warehouse_operations = get_object_or_404(WarehouseOperation, id=warehouse_operation_id)
    warehouse_operation_item = WarehouseOperationItem.objects.filter(warehouse_operation_id=warehouse_operation_id).values("product__name","product_variable_id", "product_variable__color__name", 'product_variable__measure_item__name').annotate(
        total_amount=Coalesce(Sum("amount"), 0)
    )
    return render(request, 'driver/warehouse/operation/details/by_product.html',
                  {"d": driver, 'warehouse_operation_item': warehouse_operation_item})



