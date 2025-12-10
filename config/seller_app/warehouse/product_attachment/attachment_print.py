from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.db.models import Count
from order.models import Order, OrderProduct
from services.seller.get_seller import get_seller
from store.models import ProductVariable, Product
from user.models import Regions
from django.core.cache import cache

from django.db.models.functions import Coalesce
from django.db.models import Sum, Count, Q

@login_required(login_url='/login')
@permission_required('admin.seller_app_warehouse_product_attachment_history', login_url="/home")
def seller_app_warehouse_product_attachment_print(request):
    region = Regions.objects.all()
    seller = get_seller(request.user)
    products = cache.get_or_set("product_list_cache", Product.objects.filter(seller=seller))
    return render(request, 'seller_app/warehouse/product_attachment/print/print.html', {"region":region, "products":products})
    # return render(request, 'order/print/test.html', {"region":region, 'products':products})


@login_required(login_url='/login')
@permission_required('admin.seller_app_warehouse_product_attachment_history', login_url="/home")
def seller_app_warehouse_product_attachment_packaging_order_print(request):
    region = Regions.objects.all()
    seller = get_seller(request.user)
    products = cache.get_or_set("product_list_cache", Product.objects.filter(seller=seller))
    return render(request, 'seller_app/warehouse/product_attachment/print/packaging_order_print.html', {"region":region, "products":products})




@permission_required('admin.seller_app_warehouse_product_attachment_history', login_url="/home")
def seller_app_warehouse_product_attachment_print_api(request):
    status = request.GET.get("status", 7)
    seller = get_seller(request.user)
    orders = Order.objects.filter(seller=seller, status=status).order_by("id")
    # mahsulot bo'yicha nechta order borligini tekshirish
    # a mahsulotga nechta zakaz keldi, nechtaga chop etildi
    order_product = OrderProduct.objects.filter(order__seller=seller,order__status=status, product_type__in=[1, 2]).values("product_id", "product__name").annotate(
        total_order_amount=Coalesce(Sum("total_quantity"), 0),
    ).order_by("-total_order_amount")

    region = request.GET.get("region", None)
    if region not in {None, "0"}:
        orders = orders.filter(customer_region_id=region)

    product = request.GET.get("product", None)
    if product not in {None, "0"}:
        orders = orders.filter(orderproduct__product_type__in=[1, 2], orderproduct__product_id=product)

    is_print = request.GET.get("is_print", None)
    if is_print not in {None, "0"}:
        orders = orders.filter(is_print={"1": False, "2": True}.get(is_print))

    page_number = request.GET.get('page', 1)
    order_length = request.GET.get('order_length', 50)
    paginator = Paginator(orders, order_length)
    page = paginator.get_page(page_number)

    def get_object_name_or_none(obj):
        if obj:
            return obj.name
        return None

    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        Order.objects.filter(seller=seller, id__in=body['orders_id']).update(status=8)
        return JsonResponse({
            'status': 200,
        })
    order_list = []
    def get_or_None(obj):
        if obj:
            obj.barcode
        return None



    for i in page.object_list:
        operator = ''
        if i.operator is not None:
            operator = i.operator.username
        else:
            operator = seller.username
        data = {"id":i.id, 'barcode':i.barcode,
                'is_print':i.is_print,
                'operator':operator,
                'customer_name':i.customer_name, 'is_there_previous_order':get_or_None(i.is_there_previous_order),
                'customer_phone':i.customer_phone, 'customer_phone2':i.customer_phone2,
                'customer_region':i.customer_region.name if i.customer_region is not None else '',
                'customer_district':i.customer_district.name if i.customer_district is not None else '',
                'customer_street':i.customer_street,
                "total_price": i.total_product_price}

        product_list = []
        for p in i.order_products:

            if p.product_type == '1':
                if p.product_variable:
                    product_list.append({"type":p.product_type,"product_name":p.product.name, "color":get_object_name_or_none(p.product_variable.color), "measure_item":get_object_name_or_none(p.product_variable.measure_item), 'price':p.price_uzs, 'amount':p.total_quantity})
                else:
                    product_list.append(
                        {"type":p.product_type,"product_name": p.product.name, "color": '',
                         "measure_item": '', 'price': p.total_price,
                         'amount': p.total_quantity})

            else:
                collection_items = [{"product_name":item.product.name,
                                     "color":get_object_name_or_none(item.product_variable.color),
                                     "measure_item":get_object_name_or_none(item.product_variable.measure_item)} for item in OrderProduct.objects.filter(main_order_product=p)]
                product_list.append(
                    {"type":p.product_type,"product_name": p.product.name, "color": '',
                     "measure_item": '', 'price': p.total_price,
                     'amount': p.total_quantity,
                     "collection_items":collection_items
                     })
        data['product_list'] = product_list
        order_list.append(data)
    return JsonResponse({
        'status':200,
        'data': order_list,
        'order_count': len(order_list),
        'total_order_count': orders.count(),
        'total_printed_order_count': orders.filter(is_print=True).count(),
        'total_unprinted_order_count': orders.filter(is_print=False).count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,
        'order_products': list(order_product),
    })
