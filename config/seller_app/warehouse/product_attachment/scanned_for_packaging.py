import json

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from services.order.history import save_order_status_history
from warehouse.models import WareHouse
from services.seller.get_seller import get_seller
from order.models import Order, OrderProduct


@login_required(login_url='/login')
@permission_required('admin.seller_app_warehouse_product_attachment_history', login_url="/home")
def seller_app_warehouse_product_attachment_scanned_for_packaging(request):
    seller = get_seller(request.user)
    warehouse = get_object_or_404(WareHouse, responsible=seller, type='1')
    return render(request, 'seller_app/warehouse/product_attachment/scanned_for_packaging.html', {'seller':seller, 'warehouse':warehouse})







@permission_required('admin.seller_app_warehouse_product_attachment_history', login_url="/home")
def seller_app_warehouse_product_attachment_scanned_for_packaging_api(request):
    status = request.GET.get("status", 7)
    seller = get_seller(request.user)
    warehouse = get_object_or_404(WareHouse, responsible=seller, type='1')
    orders = Order.objects.filter(seller=seller, status='2').order_by("id")
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
        barcode = body['barcode']

        order = Order.objects.filter(barcode=barcode).first()
        if not order:
            return JsonResponse({
                'status': 404,
                'message': "Bunday buyurtma mavjud emas",
            })

        if order and order.status == '2':
            return JsonResponse({
                'status': 404,
                'message': f"Ushbu buyurtma skannerlab bo'lingan",
            })

        if order and order.status != '8':
            return JsonResponse({
                'status': 404,
                'message': f"Ushbu buyurtma qadoqlanmoqda holatida emas bu buyurtma {order.get_status_display()} holatida",
            })

        order.status = '2'
        order.save()

        save_order_status_history(order, order.status,
                                  "Buyurtma skannerlab yuborishga tayyorga o'tkazildi",
                                  request.user,
                                  'config.warehouse.product_attachment.scanned_for_packaging')
        return JsonResponse({
            'status': 200,
            'message': "Tasdiqlandi"
        })
    order_list = []
    def get_or_None(obj):
        if obj:
            obj.barcode
        return None

    for i in page.object_list:
        data = {"id":i.id, 'barcode':i.barcode,
                'is_print':i.is_print,
                'customer_name':i.customer_name, 'is_there_previous_order':get_or_None(i.is_there_previous_order),
                'customer_phone':i.customer_phone, 'customer_phone2':i.customer_phone2,
                'customer_region':i.customer_region.name if i.customer_region is not None else '',
                'customer_district':i.customer_district.name if i.customer_district is not None else '',
                'customer_street':i.customer_street,
              "total_price":i.total_product_price}

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
    print(order_list)
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
