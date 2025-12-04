import json
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, redirect
from order.models import Order, OrderProduct
from order.services.calculate_operator_fee import calculate_operator_fee
from django.contrib import messages
from config.operator_app.permission import check_work_hours
from django.http import JsonResponse

from order.services.crud_service import OrderCrudService
from services.handle_exception import handle_exception
from services.order.history import save_order_status_history
from services.seller.get_seller import get_seller
from user.models import Regions, Districts
from django.db import transaction, IntegrityError
from datetime import timedelta
from datetime import datetime
import logging
from config.settings.base import OPERATOR_BONUS_FOR_ADDITIONAL_SOLD
from store.services.product_list import ProductListService
from order.services.client_report import ClientReportService

developer_logger = logging.getLogger('developer_logger')






@login_required(login_url='/login')
@permission_required('admin.operator_app_order_details', login_url="/home")
@check_work_hours
def operator_app_order_details(request, id):
    seller = get_seller(request.user)
    order = Order.objects.filter(id=id, operator=request.user, status__in=[9, 6]).first()
    if not order:
        messages.error(request, "Buyurtma topilmadi")
        return redirect("operator_app_my_order")
    if request.user.type == "3":
        operator_standard_fee = request.user.special_fee_amount
    else:
        operator_standard_fee = 4000
    client_phone_services = ClientReportService()
    client_phone_history = client_phone_services.get_client_phone_order_history(order.customer_phone)
    product_list_service = ProductListService()
    order_crud_services = OrderCrudService()
    selected_products_list = order_crud_services.get_order_product_product_json(id)
    all_products_json = product_list_service.get_product_json_by_site(seller=seller)
    if request.method == "POST":
        try:
            with transaction.atomic():
                operator = request.user
                r = request.POST
                d = json.loads(r["products"])
                order = Order.objects.get(id=id)
                order.status = 1
                order.customer_name = r['customer_name']
                order.customer_phone2 = r['customer_phone2']
                order.customer_region_id = r['region']
                order.customer_district_id = r['district']
                order.customer_street = r['street']
                # order.operator_note = r['operator_note']
                order.delivered_date = r['delivered_date']
                order.operator_status_changed_at = datetime.now()
                OrderProduct.objects.filter(order_id=r['order_id']).delete()
                order_crud_services.order_product_create(order, d)
                operator_fee_amount = calculate_operator_fee(OrderProduct.objects.filter(order_id=r['order_id']), operator_standard_fee)
                order.operator_fee=operator_fee_amount
                order.save()
                order.update_product_total_price()
                order.update_product_total_quantity()
                save_order_status_history(order, order.status, "Operator buyurtmani qabul qildi", request.user,
                                          'config.operator_app.order.details')
                messages.success(request, "Buyurtma qabul qilindi")
                return redirect('operator_app_my_order')
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Ma'lumotlar saqlashda hatolik {e}")
            return redirect('operator_app_my_order')
    return render(request, 'operator_app/order/details.html', {
        "all_products_json": json.dumps(all_products_json),
        "selected_products_json": json.dumps(selected_products_list),
        "client_phone_history": client_phone_history,
        "order": order,
        "region_list": list(Regions.objects.all().values("id", "name")),
        "district_list": json.dumps(list(Districts.objects.filter(is_active=True).values("id", "name", "region_id"))),
        "selected_region": order.customer_region.id if order.customer_region else 0,
        "selected_district": order.customer_district.id if order.customer_district else 0,
        "selected_district_obj": {'id': order.customer_district.id, "name": order.customer_district.name,
                                  'region_id': order.customer_district.region_id} if order.customer_district else 0,
        'default_delivered_date': datetime.today() + timedelta(days=2),
        'operator_standard_fee': operator_standard_fee,
        'operator_bonus_for_additional_sold': OPERATOR_BONUS_FOR_ADDITIONAL_SOLD,

    })
