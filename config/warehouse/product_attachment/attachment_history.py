import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib import messages

from services.order.history import save_order_status_history
from warehouse.models import  WareHouseStock
from django.db.models import Count, Sum, Q
from store.models import ProductVariable, ProductCollectionItem
from order.models import Order, OrderProduct
from django.db.models.functions import Coalesce
from django.db import transaction, IntegrityError
from services.warehouse.purchase.purchase_services import PurchaseProductServices
from user.models import Regions
from warehouse.models import WarehouseOperation, WareHouseStock, WareHouse
from collections import defaultdict


def warehouse_stock_check_and_minus_new(order_list):
    checked_orders = []
    unchecked_orders = []
    all_products = set(product['product_variable_id'] for order in order_list for product in order['order_product'])
    warehouse_stock = WareHouseStock.objects.filter(warehouse_id=1, product_variable_id__in=all_products, attachment_amount__gt=0).select_for_update()
    product_stock_amounts = {w['product_variable_id']:w['attachment_amount'] for w in warehouse_stock.values("product_variable_id", "attachment_amount")}
    for order in order_list:
        order_id = order['order_id']
        order_products = order['order_product']
        enough_stock = True
        
        for product in order_products:
            product_variable_id = product['product_variable_id']
            amount = int(product['ordered_amount'])
            product_stock_amount = int(product_stock_amounts.get(int(product_variable_id), 0))
            if amount <= 0 or amount > product_stock_amount:
                enough_stock = False
                continue
            
        if enough_stock:
            for product in order_products:
                product_variable_id = product['product_variable_id']
                amount = product['ordered_amount']
                product_stock_amounts[int(product_variable_id)] -= amount  # Stoktan düşme işlemi
            checked_orders.append(order_id)
        else:
            unchecked_orders.append(order_id)
    for s in product_stock_amounts:
        warehouse_stock.filter(product_variable_id=s).update(attachment_amount=product_stock_amounts.get(s))
    return checked_orders




@login_required(login_url='/login')
@permission_required('admin.warehouse_product_attachment_history', login_url="/home")
def warehouse_product_attachment_history(request):
    # order_statistic = Order.objects.exclude(customer_region_id__in=cancelled_region).filter(Q(orderproduct__type__in=[1, 3], orderproduct__product_variable__isnull=False), status__in=[1, 7, 8]).aggregate(
    order_statistic = Order.objects.aggregate(
        # product_pending=Count('id', filter=Q(status=1)),
        product_checked=Count('id', filter=Q(status=7)),
        product_being_packed=Count('id', filter=Q(status=8)),
    )
    order_statistic['product_pending'] = Order.objects.filter(status=1).count()

    purchase_product_services = PurchaseProductServices()
    status = request.GET.get("status", 1)
    
    attachment_amount_inventory = request.GET.get("attachment_amount_inventory", None)
    if attachment_amount_inventory:
        # birinchi driver omboridagi attachment amountlarni tekshirib chiqish
        try:
            with transaction.atomic():
                stock = WareHouseStock.objects.filter(warehouse_id=1).update(attachment_amount=F("amount"))
                order_products = OrderProduct.objects.filter(product_type__in=[1, 3],
                                                             order__status__in=[7, 8]).values(
                    "product_variable_id").annotate(
                    unit_amount=Coalesce(Sum("total_quantity", filter=Q(product_type=1)), 0),
                    collection_amount=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type=3)), 0),
                    ordered_amount=F('unit_amount') + F("collection_amount"),
                )
                order_products_dict = defaultdict(int)
                for order_product in order_products:
                    order_products_dict[order_product['product_variable_id']] += order_product['ordered_amount']
                # Sözlüğü normal dict'e dönüştürme (opsiyonel)
                order_products_dict = dict(order_products_dict)

                for s in order_products_dict:
                    WareHouseStock.objects.filter(warehouse_id=1, product_variable_id=s).update(
                        attachment_amount=F('attachment_amount') - order_products_dict.get(s))

                messages.success(request, "To'g'irlandi")
                return redirect("warehouse_product_attachment_history")
        except Exception as e:
            messages.error(request, f"Xatolik : {e}")
            return redirect("warehouse_product_attachment_history")

    status_by_product_list = []
    status_by_collection_product_list = []
    status = request.GET.get("status", 1)
    type = int(request.GET.get("type", 1))
    region = request.GET.get("region", None)
    region = None if region in [None, '0', 0] else region

    if type == 2:
        status_by_product_list = purchase_product_services.get_unit_product_and_collection(status, region)
    elif type == 1:
        status_by_product_list = purchase_product_services.get_product_variable_list(status, region)

            
    clear_check_product = request.GET.get("clear_check_product", None)
    if clear_check_product:
        try:
            with transaction.atomic():
                orders = Order.objects.filter(status=7).select_for_update()
                for order in orders:
                    order_products = OrderProduct.objects.filter(order_id=order.id, product_variable__isnull=False).values(
                        "product_variable_id").annotate(
                        unit_amount=Coalesce(Sum("total_quantity", filter=Q(product_type=1)), 0),
                        collection_amount=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type=3)), 0),
                        ordered_amount=F('unit_amount') + F("collection_amount"),
                    )
                    for order_product in order_products:
                        stock = WareHouseStock.objects.select_for_update().get(warehouse_id=1,
                                                      product_variable_id=order_product['product_variable_id'])

                        old_attachment_amount = int(stock.attachment_amount) + int(order_product['ordered_amount'])
                        if stock.amount < old_attachment_amount:
                            stock.attachment_amount = stock.amount
                        else:
                            stock.attachment_amount = old_attachment_amount
                        stock.save()    
                            
                    order.status=1
                    order.save()

                    save_order_status_history(order, order.status,
                                              "Buyurtma xodim tarafidan qabul qilindiga olindi",
                                              request.user,
                                              'config.warehouse.product_attachment.attachment_history')
                messages.success(request, "Saqlanmoqda")
                return redirect("warehouse_product_attachment_history")
        except IntegrityError:
            messages.error(request, "Mahsulot kutilmoqdaga o'tkazildi")
            return redirect('warehouse_product_attachment_history')

    clear_being_packed = request.GET.get("clear_being_packed", None)
    if clear_being_packed:
        try:
            with transaction.atomic():
                orders = Order.objects.filter(status=8).select_for_update()
                for order in orders:
                    order_products = OrderProduct.objects.filter(order_id=order.id, product_variable__isnull=False).values(
                        "product_variable_id").annotate(
                        unit_amount=Coalesce(Sum("total_quantity", filter=Q(product_type=1)), 0),
                        collection_amount=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type=3)), 0),
                        ordered_amount=F('unit_amount') + F("collection_amount"),
                    )
                    for order_product in order_products:
                        # WareHouseStock.objects.filter(warehouse_id=1, product_variable_id=order_product['product_variable_id']).update(
                        #     attachment_amount=F("attachment_amount") + int(order_product['ordered_amount']))
                            
                        stock = WareHouseStock.objects.select_for_update().get(warehouse_id=1,
                                                      product_variable_id=order_product['product_variable_id'])

                        old_attachment_amount = int(stock.attachment_amount) + int(order_product['ordered_amount'])
                        if stock.amount < old_attachment_amount:
                            stock.attachment_amount = stock.amount
                        else:
                            stock.attachment_amount = old_attachment_amount
                        stock.save()

                    order.status=1
                    order.save()
                    save_order_status_history(order, order.status,
                                              "Buyurtma xodim tarafidan qabul qilindiga olindi",
                                              request.user,
                                              'config.warehouse.product_attachment.attachment_history')
                messages.success(request, "Mahsulot kutilmoqdaga o'tkazildi")
                return redirect("warehouse_product_attachment_history")
        except IntegrityError:
            messages.error(request, "Sizda xatolik mavjud")
            return redirect('warehouse_product_attachment_history')



    # product_auto_attachment = request.GET.get("create_new_attachment", None)
    # if product_auto_attachment:
    product_auto_attachment = request.GET.get("region_attachment", None)
        # product_auto_attachment = request.GET.get("create_new_attachment", None)
    if product_auto_attachment:
        try:
            with transaction.atomic():

                if product_auto_attachment == '0':
                    orders = Order.objects.filter(status=1).order_by('id')
                else:
                    orders = Order.objects.filter(status=1, customer_region_id=int(product_auto_attachment)).order_by("id")

                paginator = Paginator(orders, 50)
                for page_num in paginator.page_range:
                    page_orders = paginator.page(page_num)
                    order_list = []
                    for o in page_orders.object_list:
                        order_products = OrderProduct.objects.filter(order_id=o.id, product_variable__isnull=False).values("product_variable_id").annotate(
                            unit_amount=Coalesce(Sum("total_quantity", filter=Q(product_type=1)), 0),
                            collection_amount=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type=3)), 0),
                            ordered_amount=F('unit_amount')+F("collection_amount"),
                        )
                        order_list.append({"order_id":o.id, "order_product":list(order_products)})
                    Order.objects.filter(id__in=warehouse_stock_check_and_minus_new(order_list)).update(status=7)
                messages.success(request, "Belgilandi")
                return redirect("warehouse_product_attachment_history")
        except IntegrityError:
            messages.error(request, "Sizda xatolik mavjud")
            return redirect('warehouse_product_attachment_history')

    regions = Regions.objects.all()
    return render(request, 'warehouse/product_attachment/main.html', {'regions':regions,'order_statistic':order_statistic, "status_by_product_list":status_by_product_list,
    'status_by_collection_product_list':status_by_collection_product_list})
    
    
    
    
    
    
    
    
    
    
    