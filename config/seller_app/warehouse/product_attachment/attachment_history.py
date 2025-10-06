import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib import messages

from services.handle_exception import handle_exception
from services.order.history import save_order_status_history
from services.seller.get_seller import get_seller
from warehouse.models import WareHouseStock, WarehouseStockAttachmentOrder, OrderWarehouseAction
from django.db.models import Count, Sum, Q
from store.models import ProductVariable, ProductCollectionItem
from order.models import Order, OrderProduct
from django.db.models.functions import Coalesce
from django.db import transaction, IntegrityError
from services.warehouse.purchase.purchase_services import PurchaseProductServices
from user.models import Regions
from warehouse.models import WarehouseOperation, WareHouseStock, WareHouse
from collections import defaultdict
from django.db import transaction
from django.contrib.contenttypes.models import ContentType


def warehouse_stock_check_and_create_action(warehouse, order_list, user):
    checked_orders = []
    unchecked_orders = []

    all_products = set(product['product_variable_id'] for order in order_list for product in order['order_product'])

    with transaction.atomic():
        # select_for_update ile stokları kilitle
        stocks = WareHouseStock.objects.select_for_update().filter(
            warehouse=warehouse,
            product_variable_id__in=all_products,
            status="1",  # sadece stokta olanlar
            quantity__gt=0
        ).order_by("lot_number")

        # {product_variable_id: [stoklar]}
        stock_map = {}
        for stock in stocks:
            stock_map.setdefault(stock.product_variable_id, []).append(stock)

        for order in order_list:
            order_id = order['order_id']
            order_products = order['order_product']
            enough_stock = True
            deduction_plan = []  # [(stock_obj, quantity_to_deduct)]

            for product in order_products:
                pv_id = product['product_variable_id']
                required_amount = int(product['ordered_amount'])

                available_stocks = stock_map.get(pv_id, [])
                total_available = sum(s.quantity for s in available_stocks)

                if total_available < required_amount:
                    enough_stock = False
                    break

                amount_left = required_amount
                for stock in available_stocks:
                    if amount_left == 0:
                        break
                    take = min(amount_left, stock.quantity)
                    deduction_plan.append((stock, take))
                    amount_left -= take

            if enough_stock:
                # create OrderWarehouseAction
                action = OrderWarehouseAction.objects.create(
                    warehouse=warehouse,
                    order_id=order_id,
                    responsible=user,
                    type="out"
                )

                for stock, take in deduction_plan:
                    # Eski stok artık kullanılmayacak
                    stock.status = "0"  # not_stock
                    stock.save()

                    # Sipariş için ayrılan miktar
                    WareHouseStock.objects.create(
                        action_type='3',
                        source_stock=stock,
                        product=stock.product,
                        order_id=order_id,
                        product_variable=stock.product_variable,
                        input_price=stock.input_price,
                        lot_number=stock.lot_number,
                        quantity=take,
                        status="2",  # ordered
                        generic_model_name="OrderWarehouseAction",
                        generic_model_id=action.id,
                    )

                    remaining_qty = stock.quantity - take
                    if remaining_qty > 0:
                        # Kalan miktarı yeni stok olarak oluştur
                        WareHouseStock.objects.create(
                            action_type='5',
                            source_stock=stock,
                            product=stock.product,
                            warehouse=stock.warehouse,
                            product_variable=stock.product_variable,
                            input_price=stock.input_price,
                            lot_number=stock.lot_number,
                            quantity=remaining_qty,
                            status="1",  # still in stock
                        )

                checked_orders.append(order_id)
            else:
                unchecked_orders.append(order_id)

    return checked_orders


def warehouse_stock_order_attachment_attached_calculate_warehouse(warehouse):
    warehouse_stock_qs = WareHouseStock.objects.filter(
        status='1',
        warehouse=warehouse
    ).values(
        'product_variable_id'
    ).annotate(
        quantity=Sum('quantity'),
        product_id=Sum('product_id')
    )
    for i in warehouse_stock_qs:
        WarehouseStockAttachmentOrder.objects.update_or_create(
            warehouse=warehouse,
            product_variable_id=i['product_variable_id'],
            defaults={
                "warehouse_quantity":i['quantity'],
                "attachment_amount":i['quantity'],
                "product_id":i['product_id'],
            }
        )
    return True


def order_products_return_warehouse(order, warehouse, user):
    order_warehouse_action = OrderWarehouseAction.objects.create(
        order=order,
        warehouse=warehouse,
        responsible=user,
        type='return'
    )
    warehouse_stocks_order = WareHouseStock.objects.filter(order=order, status="2")
    for stock in warehouse_stocks_order:
        WareHouseStock.objects.create(
            action_type="4",
            source_stock=stock,

            warehouse=warehouse,
            product=stock.product,
            product_variable=stock.product_variable,
            status='1',
            quantity=stock.quantity,
            input_price=stock.input_price,
            lot_number=stock.lot_number,
            generic_model_name="OrderWarehouseAction",
            generic_model_id=order_warehouse_action.id,
        )
        stock.order = None
        stock.status = "0"
        stock.save()


@login_required(login_url='/login')
@permission_required('admin.seller_app_warehouse_product_attachment_history', login_url="/home")
def seller_app_warehouse_product_attachment_history(request):
    seller = get_seller(request.user)
    # order_statistic = Order.objects.exclude(customer_region_id__in=cancelled_region).filter(Q(orderproduct__type__in=[1, 3], orderproduct__product_variable__isnull=False), status__in=[1, 7, 8]).aggregate(
    order_statistic = Order.objects.filter(seller=seller).aggregate(
        product_checked=Count('id', filter=Q(status=7)),
        product_being_packed=Count('id', filter=Q(status=8)),
        packed=Count('id', filter=Q(status=2)),
    )
    order_statistic['product_pending'] = Order.objects.filter(seller=seller, status=1).count()

    purchase_product_services = PurchaseProductServices()
    status = request.GET.get("status", 1)

    main_warehouse = WareHouse.objects.get(responsible=seller, type='1')
    # warehouse_stock_order_attachment_attached_calculate_warehouse(main_warehouse)
    status_by_product_list = []
    status_by_collection_product_list = []
    status = request.GET.get("status", 1)
    type = int(request.GET.get("type", 1))
    region = request.GET.get("region", None)
    region = None if region in [None, '0', 0] else region

    if type == 2:
        status_by_product_list = purchase_product_services.get_unit_product_and_collection(seller, status, region)
    elif type == 1:
        status_by_product_list = purchase_product_services.get_product_variable_list(seller, status, region)

            
    clear_check_product = request.GET.get("clear_check_product", None)
    if clear_check_product:
        try:
            with transaction.atomic():
                orders = Order.objects.filter(seller=seller, status=7).select_for_update()
                for order in orders:
                    order_products_return_warehouse(order, main_warehouse, request.user)
                    order.status=1
                    order.save()
                    save_order_status_history(order, order.status,
                                              "Buyurtma xodim tarafidan qabul qilindiga olindi",
                                              request.user,
                                              'config.warehouse.product_attachment.attachment_history')
                messages.success(request, "Saqlanmoqda")
                return redirect("seller_app_warehouse_product_attachment_history")
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, "Mahsulot kutilmoqdaga o'tkazildi")
            return redirect('seller_app_warehouse_product_attachment_history')

    clear_being_packed = request.GET.get("clear_being_packed", None)
    if clear_being_packed:
        try:
            with transaction.atomic():
                orders = Order.objects.filter(seller=seller, status=8).select_for_update()
                for order in orders:
                    order_products_return_warehouse(order, main_warehouse, request.user)
                    order.status=1
                    order.save()
                    save_order_status_history(order, order.status,
                                              "Buyurtma xodim tarafidan qabul qilindiga olindi",
                                              request.user,
                                              'config.warehouse.product_attachment.attachment_history')
                messages.success(request, "Mahsulot kutilmoqdaga o'tkazildi")
                return redirect("seller_app_warehouse_product_attachment_history")
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, "Sizda xatolik mavjud")
            return redirect('seller_app_warehouse_product_attachment_history')

    clear_being_packed = request.GET.get("clear_ready_to_send", None)
    if clear_being_packed:
        try:
            with transaction.atomic():
                orders = Order.objects.filter(seller=seller, status=2).select_for_update()
                for order in orders:
                    # order_products_return_warehouse(order, main_warehouse, request.user)
                    order.status='8'
                    order.save()
                    save_order_status_history(order, order.status,
                                              "Buyurtma xodim tarafidan qabul qilindiga olindi",
                                              request.user,
                                              'config.warehouse.product_attachment.attachment_history')
                messages.success(request, "Mahsulot kutilmoqdaga o'tkazildi")
                return redirect("seller_app_warehouse_product_attachment_history")
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, "Sizda xatolik mavjud")
            return redirect('seller_app_warehouse_product_attachment_history')

    product_auto_attachment = request.GET.get("region_attachment", None)
    if product_auto_attachment:
        try:
            with transaction.atomic():

                if product_auto_attachment == '0':
                    orders = Order.objects.filter(seller=seller, status=1).order_by('id')
                else:
                    orders = Order.objects.filter(status=1, seller=seller, customer_region_id=int(product_auto_attachment)).order_by("id")

                paginator = Paginator(orders, 50)
                for page_num in paginator.page_range:
                    page_orders = paginator.page(page_num)
                    order_list = []
                    for o in page_orders.object_list:
                        print('pagination', o)
                        order_products = OrderProduct.objects.filter(order_id=o.id, product_variable__isnull=False).values("product_variable_id").annotate(
                            unit_amount=Coalesce(Sum("total_quantity", filter=Q(product_type=1)), 0),
                            collection_amount=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type=3)), 0),
                            ordered_amount=F('unit_amount')+F("collection_amount"),
                        )
                        order_list.append({"order_id":o.id, "order_product":list(order_products)})
                    # Order.objects.filter(id__in=warehouse_stock_check_and_minus_new(main_warehouse, order_list), seller=seller).update(status=7)
                    Order.objects.filter(id__in=warehouse_stock_check_and_create_action(main_warehouse, order_list, request.user), seller=seller).update(status=7)
                messages.success(request, "Belgilandi")
                return redirect("seller_app_warehouse_product_attachment_history")
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, "Sizda xatolik mavjud")
            return redirect('seller_app_warehouse_product_attachment_history')
        except Exception as e:
            handle_exception(e)
            messages.error(request, "Sizda xatolik mavjud")
            return redirect('seller_app_warehouse_product_attachment_history')

    regions = Regions.objects.all()
    return render(request, 'seller_app/warehouse/product_attachment/main.html', {'regions':regions,
                                                                      'order_statistic':order_statistic,
                                                                      "status_by_product_list":status_by_product_list,
                                                                        'status_by_collection_product_list':status_by_collection_product_list})
    
    
    
    
    
    
    
    
    
    
    