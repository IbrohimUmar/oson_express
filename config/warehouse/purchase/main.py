from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

from services.warehouse.purchase.purchase_services import PurchaseProductServices
from store.models import Product
from config.format_money import format_money


@login_required(login_url='/login')
@permission_required('admin.warehouse_purchase_main', login_url="/home")
def warehouse_purchase_main(request):
    most_purchase_list = []
    purchase_services = PurchaseProductServices()
    if int(request.GET.get("type", 0)) == 0:
        most_purchase_list = purchase_services.get_product_waited_product_variable_count

    if int(request.GET.get("type", 0)) == 2:
        most_purchase_list = sorted(filter(lambda x: x['need_to_buy'] > 0, purchase_services.get_product_waited_product_variable_count),
                               key=lambda x: x['need_to_buy'], reverse=True)

    return render(request, 'warehouse/purchase/main.html', {'most_purchase_list':most_purchase_list})