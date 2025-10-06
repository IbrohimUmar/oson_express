from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F

from services.seller.get_seller import get_seller
from warehouse.models import WareHouse, WareHouseStock, WarehouseOperation
from config.seller_app.warehouse.permission import warehouse_permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
import datetime
import json


def add_interest(principal, rate=5):
    if principal is None or principal == 0:
        return 0
    interest = principal * rate / 100
    total_amount = principal + interest
    return total_amount


@login_required(login_url='/login')
@warehouse_permission_required('transit_product')
def seller_app_warehouse_operation_transit_product(request, warehouse_id):
    seller = get_seller(request.user)
    warehouse = get_object_or_404(WareHouse, id=warehouse_id, responsible=seller)

    if request.method == "POST":
        try:
            with transaction.atomic():
                r = request.POST
                products = json.loads(request.POST["products"])
                to_warehouse = WareHouse.objects.get(id=r['warehouse'], responsible=seller)
                warehouse_operation = WarehouseOperation.objects.create(
                    action='1', status=r['status'],
                    desc=r['desc'],
                    status_changed_user=request.user,
                    status_changed_at=datetime.datetime.now(),
                    seller=seller,
                    from_warehouse=warehouse,
                    to_warehouse_id=r['warehouse']
                )
                '''
                harbir mahsulotni check qiladi agar omborda bo'lmasal boshidan kiritishi kerak
                
                '''
                for p in products:
                    product_variable_id = p["product_variable_id"]
                    quantity_to_transfer = int(p["checked_amount"])
                    if quantity_to_transfer <= 0:
                        continue

                    available_stocks = WareHouseStock.objects.filter(
                        warehouse=warehouse,
                        product_variable=product_variable_id,
                        status="1"  # in_stock
                    ).order_by('lot_number')  # FIFO mantığı
                    total_available = available_stocks.aggregate(
                        total=Sum('quantity')
                    )['total'] or 0
                    #
                    if total_available < quantity_to_transfer:
                        raise Exception(
                            f"{p['product__name']} uchun yetarli mahsulot yo'q. Talab: {quantity_to_transfer}, mavjud: {total_available}"
                        )

                    remaining_qty = quantity_to_transfer
                    for stock in available_stocks:

                        if remaining_qty <= 0:
                            break

                        if stock.quantity <= remaining_qty:
                            # Tüm stoğu transfer ediyoruz
                            stock.status = "0"  # not_stock yap
                            stock.save()

                            WareHouseStock.objects.create(
                                action_type='2',
                                source_stock=stock,
                                warehouse_operation=warehouse_operation,
                                warehouse=to_warehouse,
                                product=stock.product,
                                product_variable=stock.product_variable,
                                quantity=stock.quantity,
                                input_price=stock.input_price,
                                lot_number=stock.lot_number,
                                status=str(int(r['status'])-1)
                            )

                            remaining_qty -= stock.quantity
                        else:
                            # Sadece bir kısmı transfer edilecek
                            # Mevcut stoğu kapat
                            stock.status = "0"
                            stock.save()

                            # Y depoya giden parça
                            WareHouseStock.objects.create(
                                action_type='2',
                                source_stock=stock,
                                warehouse_operation=warehouse_operation,
                                warehouse=to_warehouse,
                                product=stock.product,
                                product_variable=stock.product_variable,
                                quantity=remaining_qty,
                                input_price=stock.input_price,
                                lot_number=stock.lot_number,
                                status=str(int(r['status'])-1)
                            )
                            # X depoda kalan parça
                            WareHouseStock.objects.create(
                                action_type='6',
                                source_stock=stock,
                                warehouse=warehouse,
                                product=stock.product,
                                product_variable=stock.product_variable,
                                quantity=stock.quantity - remaining_qty,
                                input_price=stock.input_price,
                                lot_number=stock.lot_number,
                                status='1'
                            )
                            remaining_qty = 0
                messages.success(request, f"Ma'lumotlar saqlandi")
                return redirect('seller_app_warehouse_list')
        except IntegrityError as e:
            messages.error(request, f"Sizda hatolik {e}")
            return redirect('seller_app_warehouse_list')

    warehouse_list = WareHouse.objects.filter(responsible=seller).exclude(id=warehouse_id)
    warehouse_stock_qs = WareHouseStock.objects.filter(
        status='1',
        warehouse=warehouse
    ).values(
        'product_variable_id',
        'product_variable__measure_item__name',
        'product_variable__color__name',
    ).annotate(
        quantity=Sum('quantity'),
        product__name=F('product__name'),
        product_id=F('product_id')
    )
    warehouse_stock = json.dumps([
        {
            **item,
            'checked_price': 0,
            'checked_amount': 0,
            'is_check': 0,
            'input_price': 0,
        }
        for item in warehouse_stock_qs
    ])
    return render(request, 'seller_app/warehouse/operation/transit.html', {"warehouse_list":warehouse_list, 'warehouse':warehouse, 'warehouse_stock':warehouse_stock})
