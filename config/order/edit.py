# import json
# from sqlite3 import IntegrityError
#
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required, permission_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.db import transaction
# from django.db.models import Q
# from django.shortcuts import get_object_or_404, redirect, render
# from config.settings.base import OPERATOR_BONUS_FOR_ADDITIONAL_SOLD
# from order.models import Order, OrderProduct
# from order.services.calculate_operator_fee import calculate_operator_fee
# from order.services.client_report import ClientReportService
# from order.services.crud_service import OrderCrudService
# from services.order.history import save_order_status_history
# from services.seller.get_seller import get_seller
# from store.services.product_list import ProductListService
# from user.models import Districts, Regions
# from datetime import datetime, timedelta, timezone
#
# import datetime
# @login_required(login_url='/login')
# @permission_required('admin.seller_app_order_edit', login_url="/home")
# def seller_app_order_edit(request, id):
#     seller = get_seller(request.user)
#     try:
#         order = get_object_or_404(Order, id=id, seller=seller, status__in=[0, 9, 10, 11, 12, 1])
#     except ObjectDoesNotExist:
#         messages.info(request, "Bu buyurtmaga mahsulot belglangan")
#         return redirect("seller_app_order_list")
#
#     if request.user.type == "3":
#         operator_standard_fee = request.user.special_fee_amount
#     else:
#         operator_standard_fee = 4000
#
#     product_list_service = ProductListService()
#     all_products_json = product_list_service.get_product_json_by_site(seller=request.user.seller)
#     client_history_services = ClientReportService()
#     order_crud_services = OrderCrudService()
#     selected_product_list = order_crud_services.get_order_product_product_json(order.id)
#
#     if request.method == "POST":
#         r = request.POST
#         try:
#             with transaction.atomic():
#                 order = Order.objects.filter(id=id, status=1).select_for_update()
#                 products = json.loads(request.POST["products"])
#                 if not order:
#                     messages.success(request, "Buyrutmani o'zgartirish mumkun emas")
#                     return redirect('operator_app_order_edit', id)
#
#                 district = Districts.objects.get(id=r['district'])
#                 order = Order.objects.get(id=id)
#                 order.customer_name = r['customer_name']
#                 order.customer_phone2 = r['customer_phone2']
#                 order.customer_region_id = r['region']
#                 order.customer_district_id = r['district']
#                 order.customer_street = r['street']
#                 order.operator_note = r['operator_note']
#                 order.delivered_date = r['delivered_date']
#                 order.driver_is_bonus = district.driver_is_bonus
#                 order.driver_one_day_bonus = district.driver_one_day_bonus
#                 order.driver_two_day_bonus = district.driver_two_day_bonus
#                 order.operator_status_changed_at = datetime.now()
#
#                 OrderProduct.objects.filter(order_id=id).delete()
#                 order_crud_services.order_product_create(order, products)
#
#                 operator_fee_amount = calculate_operator_fee(OrderProduct.objects.filter(order_id=r['order_id']), operator_standard_fee)
#                 order.operator_fee = operator_fee_amount
#                 order.save()
#                 order.update_product_total_price()
#                 order.update_product_total_quantity()
#                 order.update_driver_fee()
#                 order.update_logistic_fee()
#                 order.update_seller_fee()
#                 save_order_status_history(order, order.status, "Operator buyurtma ma'lumotlarini o'zgartirdi", request.user,
#                                           'config.operator_app.order.edit')
#                 messages.success(request, "O'zgartirildi")
#                 return redirect('operator_app_order_edit', id)
#
#         except IntegrityError as e:
#             messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
#             return redirect('operator_app_order_history')
#
#     return render(request, 'seller_app/order/edit.html',
#                   {
#                       "all_products_json": json.dumps(all_products_json),
#                       "selected_products_json": json.dumps(selected_product_list),
#                       "client_phone_history": client_history_services.get_client_phone_order_history(
#                           order.customer_phone),
#
#                       "region_list": list(Regions.objects.all().values("id", "name")),
#                       "district_list": json.dumps(
#                           list(Districts.objects.filter(is_active=True).values("id", "name", "region_id"))),
#                       "selected_region": order.customer_region.id if order.customer_region else 0,
#                       "selected_district": order.customer_district.id if order.customer_district else 0,
#
#                       "order": order,
#                       'operator_standard_fee': operator_standard_fee,
#                       'operator_bonus_for_additional_sold': OPERATOR_BONUS_FOR_ADDITIONAL_SOLD,
#
#                       "selected_district_obj": {'id': order.customer_district.id, "name": order.customer_district.name,
#                                                 'region_id': order.customer_district.region_id} if order.customer_district else 0,
#                       'default_delivered_date': datetime.datetime.today() + timedelta(days=2),
#
#                   })
