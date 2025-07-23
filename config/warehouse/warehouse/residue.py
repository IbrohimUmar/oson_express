from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from config.warehouse.permission import warehouse_permission_check
from warehouse.models import WareHouse, WareHouseStock, WarehouseOperationItemDetails

from django.contrib import messages
import datetime

from django.db.models import Sum, ExpressionWrapper, F
from django.db.models.functions import Coalesce
from django.db import models

from config.format_money import format_money
@login_required(login_url='/login')
def warehouse_residue(request, warehouse_id):
    warehouse = get_object_or_404(WareHouse, id=warehouse_id)

    if warehouse_permission_check('warehouse_operation_transit_product',request.user, warehouse_id) is False:
        messages.error(request, "Sizga kirish uchun ruxsat yo'q")
        return redirect('home')

    stock = WareHouseStock.objects.filter(warehouse=warehouse).order_by("amount")
    total_input_price = WarehouseOperationItemDetails.objects.filter(
        warehouse_stock__warehouse=warehouse,
        leave_amount__gt=0,
        warehouse_operation__to_warehouse_status="2"
    )

    total_leave_product_input_price = format_money(total_input_price.aggregate(t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("leave_amount"), output_field=models.IntegerField())) , 0))['t'])
    total_leave_product_count = stock.aggregate(t=Coalesce(Sum("amount"), 0))['t']

    if 'excel' in request.GET:
        import os
        from django.http import HttpResponse
        from config.export_excel import export_excel_from_warehouse_residue
        excel = export_excel_from_warehouse_residue(warehouse.name, total_leave_product_input_price, total_leave_product_count, stock)
        static_file_path = os.path.join(excel)
        with open(static_file_path, 'rb') as file:
            file_content = file.read()
        response = HttpResponse(file_content, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{warehouse.name} qoldig\'i sana : {datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx"'
        return response


    if request.GET.get("search", None):
        query = request.GET["search"]
        stock = stock.filter(product__name__icontains=query)
        total_input_price = total_input_price.filter(product__name__icontains=query)

    paginator = Paginator(stock, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)

    return render(request, 'warehouse/warehouse/residue.html', {"warehouse":warehouse, 'page_obj':queryset,
                                                                "total_amount":total_leave_product_count,
                                                                "total_input_price":total_leave_product_input_price})
                                                                