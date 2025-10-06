from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import IntegerField
from django.shortcuts import render, get_object_or_404
from config.seller_app.warehouse.permission import warehouse_permission_required
from services.seller.get_seller import get_seller
from warehouse.models import WareHouse, WareHouseStock
import datetime
from django.db.models import Sum, ExpressionWrapper, F
from django.db.models.functions import Coalesce


@login_required(login_url='/login')
@warehouse_permission_required('residue')
def seller_app_warehouse_residue(request, warehouse_id):
    seller = get_seller(request.user)
    warehouse = get_object_or_404(WareHouse, id=warehouse_id, responsible=seller)
    stock = WareHouseStock.objects.filter(warehouse=warehouse, status='1')

    # total_leave_product_input_price = format_money(total_input_price.aggregate(t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("leave_amount"), output_field=models.IntegerField())) , 0))['t'])
    if request.GET.get("search", None):
        query = request.GET["search"]
        stock = stock.filter(product__name__icontains=query)

    total_leave_product_input_price=total_input_price = stock.aggregate(
    total=Sum(ExpressionWrapper(F('quantity') * F('input_price'), output_field=IntegerField())))['total'] or 0
    # total_leave_product_count = stock.aggregate(t=Coalesce(Sum("quantity"), 0))['t']
    total_leave_product_count = stock.aggregate(t=Coalesce(Sum("quantity"), 0))['t']

    if 'excel' in request.GET:
        import os
        from django.http import HttpResponse
        from config.export_excel import export_excel_from_warehouse_residue
        excel = export_excel_from_warehouse_residue(warehouse.get_type_display(), total_leave_product_input_price, total_leave_product_count, stock)
        static_file_path = os.path.join(excel)
        with open(static_file_path, 'rb') as file:
            file_content = file.read()
        response = HttpResponse(file_content, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{warehouse.get_type_display()} qoldig\'i sana : {datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx"'
        return response

    paginator = Paginator(stock, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/warehouse/warehouse/residue.html', {"warehouse":warehouse, 'page_obj':queryset,
                                                                "total_amount":total_leave_product_count,
                                                                "total_input_price":total_leave_product_input_price})
                                                                