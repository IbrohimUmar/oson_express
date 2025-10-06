import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from services.handle_exception import handle_exception
from services.seller.get_seller import get_seller
from warehouse.models import WareHouse, WarehouseOperation, WareHouseStock
from store.models import ProductVariable
import json
from user.models import User
from django.db import transaction, IntegrityError
from config.seller_app.warehouse.permission import warehouse_permission_required



@login_required(login_url='/login')
@warehouse_permission_required('input_product')
def seller_app_warehouse_operation_input_product(request, warehouse_id):
    def get_last_input_price_product(id):
        from warehouse.models import WareHouseStock
        details = WareHouseStock.objects.filter(product_variable_id=id,
                                                warehouse_id=warehouse_id).last()
        if details:
            return int(details.input_price)
        else:
            return 0

    seller = get_seller(request.user)
    warehouse = get_object_or_404(WareHouse, id=warehouse_id, responsible=seller)
    supplier = User.objects.filter(is_active=True, seller=seller, type='5')
    if request.method == "POST":
        try:
            with transaction.atomic():
                products = json.loads(request.POST["products"])
                r = request.POST
                warehouse_operation = WarehouseOperation.objects.create(
                    action='2',
                    status=r['status'],
                    status_changed_user=request.user,
                    status_changed_at=datetime.datetime.now(),
                    seller=seller,
                    supplier_id=r['supplier'],
                    to_warehouse=warehouse,
                    desc=r['desc'],
                )
                for product in products:
                    WareHouseStock.objects.create(
                        action_type='1',
                        status=str(int(r['status'])-1),
                        warehouse=warehouse,
                        warehouse_operation=warehouse_operation,
                        product_id=product['product_id'],
                        product_variable_id=product['id'],
                        quantity=product['amount'],
                        input_price=product['price'],
                        lot_number=warehouse_operation.id,
                    )
            messages.success(request, f"Kirim bajarilmoqda")
            return redirect('seller_app_warehouse_list')
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Sizda hatolik {e}")
            return redirect('seller_app_warehouse_list')
    product_list = json.dumps([dict(a, price=get_last_input_price_product(a['id']), amount=0, is_check=0) for a in ProductVariable.objects.filter(product__seller=seller, product__approval_status='2', is_active=True, product__is_active=True).values("id", "product_id","product__name", "measure_item__name", "color__name")])
    return render(request, 'seller_app/warehouse/operation/input.html', {"product_list":product_list, "supplier":supplier})
