import threading
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order, OrderProduct
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator
from django.db.models import Q, F, Count

from services.seller.get_seller import get_seller
from user.models import User
import datetime
from user.models import Regions
from store.models import Product
from django.core.cache import cache
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.cache import cache

import pandas as pd




def export_excel_sold_orders(queryset):
    file_path = f'static/excel/Sotilgan buyurtmalar soni :{queryset.count()} ta, sana : {datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")}.xlsx'
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        data = []
        count = 0
        for o in queryset:
            data.append({
                "id": o.id,
                "operator": f'{o.operator.first_name} {o.operator.last_name}',
                "mijoz_ism": o.customer_name,
                "mijoz_tel": o.customer_phone,
                "viloyati": f'{o.customer_region.name}',
                "sana": o.updated_at.strftime("%Y-%m-%d_%H-%M-%S"),
                "Mahsulot": ', '.join(o.order_products.values_list("product__name", flat=True)),  # Listeyi stringe dönüştürün
                "Jami_mahsulot_soni": o.total_product_quantity,
                "Tovar_sotilgan_narxi": o.total_product_price,

                "Tovar_tan_narxi": o.total_product_input_price,
                "Haydovchi_daromadi": o.driver_fee,
                "Admin_tulov": o.seller_fee,
                "Operatorga": o.operator_fee,
                "Qoldiq": o.leave_fee,
            })
            if len(data) == 500:
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='Buyurtmalar', index=False, startrow=count * 500)
                data = []
                count += 1
        if data:
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name='Buyurtmalar', index=False, startrow=count * 500)
    return file_path


@login_required(login_url='/login')
@permission_required('admin.seller_app_orders_list_sold', login_url="/home")
def seller_app_orders_list_sold(request):
    seller = get_seller(request.user)

    orders = Order.objects.filter(status=4, seller=seller).order_by("-updated_at")
    if request.GET.get("search", None):
        query = request.GET["search"]
        orders = orders.filter(
            Q(id__contains=query) | Q(customer_phone__contains=query) | Q(driver__username=query))
    if request.GET.get("from_date", None) and request.GET.get("to_date", None):
        orders = orders.filter(updated_at__date__range=(request.GET['from_date'], request.GET['to_date']))
    if request.GET.get("region", None) not in {None, "0"}:
        orders = orders.filter(customer_region_id=request.GET['region'])

    products = cache.get_or_set("product_cache", Product.objects.filter(seller=seller))
    regions = cache.get_or_set("region_cache", Regions.objects.all())
    if request.GET.get("product", None) not in {None, "0"}:
        orders = orders.filter(orderproduct__product_id=request.GET['product'])

    if 'excel' in request.GET:
        params = request.GET.copy()
        if 'excel' in params:
            del params['excel']
        url = request.path + '?' + params.urlencode()
        messages.success(request, "Excelga export qilinmoqda...")
        # threading.Thread()
        thread = threading.Thread(target=export_excel_sold_orders,
                                  args=(orders,))
        thread.start()
        return redirect(url)

    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    order = paginator.get_page(page_number)
    return render(request, 'seller_app/orders/list/sold.html',
                  {'page_obj': order, "order": order, 'count': orders.count(), "products": products,
                   "regions": regions})

