from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

from services.seller.get_seller import get_seller
from services.warehouse.purchase.purchase_services import PurchaseProductServices
from store.models import Product
from config.format_money import format_money
from warehouse.models import WareHouse

@login_required(login_url='/login')
@permission_required('admin.seller_app_warehouse_purchase_main', login_url="/home")
def seller_app_warehouse_purchase_main(request):
    seller = get_seller(request.user)
    warehouse = WareHouse.objects.get(responsible=seller, type='1')
    most_purchase_list = []
    purchase_services = PurchaseProductServices()
    if int(request.GET.get("type", 0)) == 0:
        most_purchase_list = purchase_services.get_product_waited_product_variable_count(warehouse)
    print(most_purchase_list)
    if int(request.GET.get("type", 0)) == 2:
        most_purchase_list = sorted(filter(lambda x: x['need_to_buy'] > 0, purchase_services.get_product_waited_product_variable_count(warehouse)),
                               key=lambda x: x['need_to_buy'], reverse=True)

    return render(request, 'seller_app/warehouse/purchase/main.html', {'most_purchase_list':most_purchase_list})