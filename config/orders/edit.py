import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from services.order.history import save_order_status_history
from store.models import Product
from store.services.product_list import ProductListService
from user.models import User, Districts, MarkedDeliveryPrice, Regions
from order.models import Order, OrderProduct, Status
# from .get_order import get_product_region_by
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from datetime import datetime, timedelta, timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from warehouse.models import WareHouseStock
from django.db.models.functions import Coalesce
from order.services.client_report import ClientReportService
from order.services.crud_service import OrderCrudService
from config.settings.base import Sites, TOLL_AMOUNT, OPERATOR_BONUS_FOR_ADDITIONAL_SOLD
from user.models import Regions
from order.services.calculate_operator_fee import calculate_operator_fee






@login_required(login_url='/login')
@permission_required('admin.order_edit', login_url="/home")
def order_edit(request, id):
    order = get_object_or_404(Order.objects.exclude(status=0), id=id, status=1,driver__isnull=True, defective_product_order__isnull=True)
    product_list_service = ProductListService()
    all_products_json = product_list_service.get_product_json_by_site()
    client_history_services = ClientReportService()
    order_crud_services = OrderCrudService()
    selected_product_list = order_crud_services.get_order_product_product_json(order.id)
    if request.method == "POST":
        r = request.POST
        try:
            with transaction.atomic():
                order = Order.objects.filter(id=id, status=1).select_for_update()
                products = json.loads(request.POST["products"])
                if not order:
                    messages.success(request, "Buyrutmani o'zgartirish mumkun emas")
                    return redirect('order_list')
                district = Districts.objects.get(id=r['district'])
                order = Order.objects.get(id=id)
                order.customer_name = r['customer_name']
                order.customer_phone2 = r['customer_phone2']
                order.customer_region_id = r['region']
                order.customer_district_id = r['district']
                order.customer_street = r['street']
                order.operator_note = r['operator_note']
                order.delivered_date = r['delivered_date']
                order.driver_is_bonus = district.driver_is_bonus
                order.driver_one_day_bonus = district.driver_one_day_bonus
                order.driver_two_day_bonus = district.driver_two_day_bonus
                order.responsible = request.user
                OrderProduct.objects.filter(order_id=id).delete()
                order_crud_services.order_product_create(order, products)

                operator_fee_amount = calculate_operator_fee(OrderProduct.objects.filter(order_id=r['order_id']), order.operator.special_fee_amount)
                order.operator_fee = operator_fee_amount
                order.save()
                order.update_product_total_price()
                order.update_product_total_quantity()
                save_order_status_history(order, order.status, "Buyurtmani o'zgartirildi", request.user,
                                          'config.orders.edit')
                messages.success(request, "O'zgartirildi")
                return redirect('order_edit', id)

        except IntegrityError as e:
            messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
            return redirect('order_list')


    return render(request, 'orders/edit.html',
                  {
                   "all_products_json": json.dumps(all_products_json),
                   "selected_products_json": json.dumps(selected_product_list),
                   "client_phone_history": client_history_services.get_client_phone_order_history(order.customer_phone),

                   "region_list": list(Regions.objects.all().values("id", "name")),
                   "district_list": json.dumps(list(Districts.objects.all().values("id", "name", "region_id"))),
                   "selected_region": order.customer_region.id if order.customer_region else 0,
                   "selected_district": order.customer_district.id if order.customer_district else 0,
                      "order": order,
                      'operator_standard_fee': order.operator.special_fee_amount,
                      'operator_bonus_for_additional_sold': OPERATOR_BONUS_FOR_ADDITIONAL_SOLD,

                      "selected_district_obj": {'id': order.customer_district.id, "name": order.customer_district.name,
                                             'region_id': order.customer_district.region_id} if order.customer_district else 0,
                      'default_delivered_date': datetime.today() + timedelta(days=2),

                   })

