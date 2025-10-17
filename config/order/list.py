from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from services.order.history import save_order_status_history
from order.models import Order, OrderProduct, Status
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.db import transaction, IntegrityError

from services.seller.get_seller import get_seller
from warehouse.models import WareHouseStock
from django.db.models.functions import Coalesce
from user.models import Regions


@login_required(login_url='/login')
@permission_required('admin.order_list', login_url="/home")
def order_list(request):
    # orders = Order.objects.all().exclude(status__in=['9', '10', '11', '12', '1', '7', '8', '2']).order_by("-created_at")
    orders = Order.objects.all().exclude(status__in=['9', '10', '11', '12', '1', '7', '8', '2']).order_by("-created_at")
    region = request.GET.get("region", 'None')
    if region != 'None':
        orders = orders.filter(customer_region=region)

    status = request.GET.get("status", 'None')
    if status != 'None':
        orders = orders.filter(status=status)

    filter_query = request.GET.get("filter", None)
    if filter_query:
        orders = orders.filter(Q(id__icontains=filter_query) | Q(customer_phone__icontains=filter_query) | Q(barcode__icontains=filter_query))

    if request.method == "POST":
        r = request.POST
        try:
            with transaction.atomic():
                order = Order.objects.filter(id=r['order_id'], status__in=[7, 8]).select_for_update().first()
                if order:
                    order_products = OrderProduct.objects.filter(order_id=order.id,
                                                                 product_variable__isnull=False).values(
                        "product_variable_id").annotate(
                        unit_amount=Coalesce(Sum("total_quantity", filter=Q(product_type=1)), 0),
                        collection_amount=Coalesce(Sum("main_order_product__total_quantity", filter=Q(product_type=3)), 0),
                        ordered_amount=F('unit_amount') + F("collection_amount"),
                    )
                    for order_product in order_products:
                        WareHouseStock.objects.filter(warehouse_id=1,
                                                      product_variable_id=order_product['product_variable_id']).update(
                            attachment_amount=F("attachment_amount") + int(order_product['ordered_amount']))
                    order.status=1
                    order.save()
                    save_order_status_history(order, order.status,
                                              "Buyurtma xodim tarafidan qabul qilindiga olindi",
                                              request.user,
                                              'config.orders.my_order.order_list')
                    messages.success(request, "O'tkazildi")
                    return redirect("seller_app_orders_list_all")
        except IntegrityError as e:
            messages.error(request, f"Hatolik yuz berdi : {e}")
            return redirect('seller_app_orders_list_all')

    paginator = Paginator(orders, 50)
    order = paginator.get_page(int(request.GET.get("page", 1)))
    return render(request, 'order/list.html', {'quary': filter_query,'page_obj': order, "order": order, 'count': orders.count(),
                                                           "statuses":Status, "regions":Regions.objects.all()
                                                          })
