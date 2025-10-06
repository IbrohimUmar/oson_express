from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.db.models import Count
from order.models import Order
from services.seller.get_seller import get_seller
from store.models import ProductVariable, Product
from user.models import Regions
from django.core.cache import cache


@login_required(login_url='/login')
@permission_required('admin.seller_app_order_print_unshipped_orders', login_url="/home")
def seller_app_order_print_unshipped_orders(request):
    region = Regions.objects.all()
    products = cache.get_or_set("product_list_cache", Product.objects.all())
    return render(request, 'seller_app/orders/print/print_unshipped_orders.html', {"region":region, "products":products})
    # return render(request, 'order/print/test.html', {"region":region, 'products':products})


@permission_required('admin.seller_app_order_print_unshipped_orders', login_url="/home")
def seller_app_print_unshipped_orders_api(request):
    seller = get_seller(request.user)
    orders = Order.objects.filter(status=1,seller=seller, barcode__isnull=False, orderproduct__product_variable__isnull=False).order_by("id")
    # orders = Order.objects.filter(status=1).order_by("id")
    region = request.GET.get("region", None)
    if region not in {None, "0"}:
        orders = orders.filter(customer_region_id=region)

    product = request.GET.get("product", None)
    if product not in {None, "0"}:
        orders = orders.filter(orderproduct__product_id=product)

    order_type = request.GET.get("order_type", None)
    if order_type not in {None, "0"}:
        # 1 bo'lsa donali kelishi kerak
        if order_type == "1":
            orders = orders.annotate(orderproduct_count=Count('orderproduct'))
            orders = orders.filter(orderproduct_count=1, orderproduct__ordered_amount=1,
                                   orderproduct__product__is_collection=False).prefetch_related('orderproduct')
        if order_type == "2":
            orders = orders.filter(orderproduct__ordered_amount__gt=1, orderproduct__product__is_collection=False).prefetch_related('orderproduct')
        if order_type == "3":
            orders = orders.filter(orderproduct__product__is_collection=True).prefetch_related('orderproduct')

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
        Order.objects.filter(id__in=body['orders_id']).update(is_print=True)
        return JsonResponse({
            'status': 200,
        })
    order_list = []
    def get_or_None(obj):
        if obj:
            obj.barcode
        return None

    for i in page.object_list:
        data = {"id":i.id, 'barcode':i.barcode, 'is_print':i.is_print, 'customer_name':i.customer_name, 'is_there_previous_order':get_or_None(i.is_there_previous_order),'customer_phone':i.customer_phone, 'customer_phone2':i.customer_phone2, 'customer_region':i.customer_region.name, 'customer_district':i.customer_district.name, 'customer_street':i.customer_street,
              "total_price":i.order_products_total_price_uzs}

        product_list = []
        # for p in i.order_products:
        #
        #     if p.type == '1':
        #         if p.product_variable:
        #             product_list.append({"type":p.type,"product_name":p.product.name, "color":get_object_name_or_none(p.product_variable.color), "measure_item":get_object_name_or_none(p.product_variable.measure_item), 'price':p.price_uzs, 'amount':p.ordered_amount})
        #         else:
        #             product_list.append(
        #                 {"type":p.type,"product_name": p.product.name, "color": '',
        #                  "measure_item": '', 'price': p.price_uzs,
        #                  'amount': p.ordered_amount})
        #
        #     else:
        #         collection_items = [{"product_name":item.product.name, "color":get_object_name_or_none(item.product_variable.color), "measure_item":get_object_name_or_none(item.product_variable.color)} for item in OrderProductCollectionItem.objects.filter(order_product=p)]
        #         product_list.append(
        #             {"type":p.type,"product_name": p.product.name, "color": '',
        #              "measure_item": '', 'price': p.price_uzs,
        #              'amount': p.ordered_amount,
        #              "collection_items":collection_items
        #              })
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
    })
