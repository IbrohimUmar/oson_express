import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from services.handle_exception import handle_exception
from services.order.history import save_order_status_history
from services.seller.get_seller import get_seller
from store.services.product_list import ProductListService
from user.models import User, Districts
from order.models import Order, OrderProduct
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from order.services.client_report import ClientReportService
from order.services.crud_service import OrderCrudService
from config.settings.base import TOLL_AMOUNT, OPERATOR_BONUS_FOR_ADDITIONAL_SOLD
from user.models import Regions
from order.services.calculate_operator_fee import calculate_operator_fee




allow_edit_seller_status = [0, 9, 6, 10, 11, 12, 1]

@login_required(login_url='/login')
@permission_required('admin.seller_app_orders_edit', login_url="/home")
def seller_app_orders_edit(request, id):
    seller = get_seller(request.user)
    order = get_object_or_404(Order, id=id, status__in=allow_edit_seller_status, seller=seller)
    product_list_service = ProductListService()
    all_products_json = product_list_service.get_product_json_by_site(seller=seller)
    order_crud_services = OrderCrudService()
    selected_product_list = order_crud_services.get_order_product_product_json(order.id)

    special_fee_amount = 0
    if order.operator is not None:
       special_fee_amount = order.operator.special_fee_amount

    if request.method == "POST":
        r = request.POST
        try:
            with transaction.atomic():
                order = Order.objects.filter(id=id, status__in=allow_edit_seller_status, seller=seller).select_for_update()
                products = json.loads(request.POST["products"])
                if not order:
                    messages.success(request, "Buyrutmani o'zgartirish mumkun emas")
                    return redirect('seller_app_orders_list_all')

                if int(r['status']) not in [0, 9, 6, 10, 11, 12, 1]:
                    messages.error(request, "Ruxsat etilmagan xolat tanlagansiz")
                    return redirect('seller_app_order_edit', id)

                district = Districts.objects.get(id=r['district'])
                order = Order.objects.get(id=id)
                order.status = r['status']
                order.customer_name = r['customer_name']
                order.customer_phone2 = r['customer_phone2']
                order.customer_region_id = r['region']
                order.customer_district_id = r['district']
                order.customer_street = r['street']
                order.operator_note = r['operator_note']
                order.delivered_date = r['delivered_date']
                order.driver_is_bonus = False
                order.responsible = request.user
                OrderProduct.objects.filter(order_id=id).delete()
                order_crud_services.order_product_create(order, products)

                operator_fee_amount = calculate_operator_fee(OrderProduct.objects.filter(order_id=r['order_id']), special_fee_amount)
                order.operator_fee = operator_fee_amount
                order.save()
                order.update_product_total_price()
                order.update_product_total_quantity()
                order.update_driver_fee()
                order.update_logistic_fee()
                order.update_seller_fee()
                save_order_status_history(order, order.status, "Buyurtma seller tomonidan o'zgartirildi", request.user,
                                          'config.seller_app.orders.edit')
                messages.success(request, "O'zgartirildi")
                return redirect('seller_app_order_edit', id)

        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
            return redirect('seller_app_order_list')
    return render(request, 'seller_app/orders/edit.html',
                  {
                   "all_products_json": json.dumps(all_products_json),
                   "selected_products_json": json.dumps(selected_product_list),
                   "region_list": list(Regions.objects.all().values("id", "name")),
                   "district_list": json.dumps(list(Districts.objects.all().values("id", "name", "region_id"))),
                   "selected_region": order.customer_region.id if order.customer_region else 0,
                   "selected_district": order.customer_district.id if order.customer_district else 0,
                    "order": order,
                      'operator_standard_fee': special_fee_amount,
                      'operator_bonus_for_additional_sold': OPERATOR_BONUS_FOR_ADDITIONAL_SOLD,
                      "selected_district_obj": {'id': order.customer_district.id, "name": order.customer_district.name,
                                             'region_id': order.customer_district.region_id} if order.customer_district else 0,
                      'default_delivered_date': datetime.today() + timedelta(days=2),
                   })

