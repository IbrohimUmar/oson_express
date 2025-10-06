import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse

from order.models import Order, OrderProduct
from user.models import User
from warehouse.models import WarehouseOperation, WarehouseOperationAndOrderRelations

from order.services.order_warehouse_operation import OrderWarehouseOperationsService


def find_exact_match_orders(cancelled_orders, search_values):
    exact_match_orders = set()
    search_values_count = {value: search_values.count(value) for value in search_values}
    for order_number, values in cancelled_orders.items():
        values_count = {value: values.count(value) for value in values}
        if values_count == search_values_count:
            exact_match_orders.add(order_number)
    return exact_match_orders

def get_order_product_json_format(order_id):
    order_products = OrderProduct.objects.filter(order_id=order_id, type__in=[1, 2]).values("id", 'product_id', 'product_variable_id', 'ordered_amount', 'type')
    for i in order_products:
        if i['type'] == '2':
            i['collection'] = {item['product_id']:item['product_variable_id'] for item in OrderProduct.objects.filter(main_order_product=i['id'], type=3).values("product_id",
                                                                                                      'product_variable_id')}
    return list(order_products)
def compare_lists(list1, list2):
    matching_ids = {}

    for item1 in list1:
        for item2 in list2:
            if (item1['product_id'] == item2['product_id'] and
                item1['ordered_amount'] == item2['ordered_amount']):
                if item1['type'] == '1':
                    if item1['product_variable_id'] == item2['product_variable_id']:
                        matching_ids[item1['id']] = item2['id']
                        break
                elif item1['type'] == '2':
                    if item1['collection'] == item2['collection']:
                        matching_ids[item1['id']] = item2['id']
                        break

    return matching_ids if matching_ids else False


def find_exact_feature_match_order(cancelled_order_ids:dict ,new_order_id):
    new_order_products = get_order_product_json_format(new_order_id)
    for c in cancelled_order_ids:
        cancelled_order_product = get_order_product_json_format(c)
        compare_result = compare_lists(new_order_products, cancelled_order_product)
        if compare_result:
            order_services = OrderWarehouseOperationsService()
            check_cancelled_order_result = order_services.driver_send_barcode_create(c, new_order_id, compare_result)
            if check_cancelled_order_result:
                return c
    return None


@permission_required('admin.driver_send_barcode_main_api', login_url="/home")
def driver_send_barcode_main_api(request):
    def get_object_name_or_none(obj):
        if obj:
            return obj.name
        return None

    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        driver_id = body['driver']
        try:
            driver = User.objects.get(id=driver_id)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 404,
                'title': "Haydovchida topilmadi",
            })
        try:
            with transaction.atomic():

                allowed_districts = list(driver.allow_districts.all().values_list("id", flat=True))

                cancelled_order_queryset = Order.objects.filter(driver=driver, cancelled_status="1", status=5, output_product__isnull=True).values_list("id", flat=True)
                cancelled_orders = {i:list(OrderProduct.objects.filter(order_id=i, type__in=[1, 2]).values_list("product_id", flat=True)) for i in cancelled_order_queryset}

                new_orders = Order.objects.filter(
                    Q(orderproduct__type__in=["1", "3"], orderproduct__product_variable__isnull=False), status=1, customer_region_id=driver.region_id, customer_district_id__in=allowed_districts).order_by("id").values("id")
                paginator = Paginator(new_orders, 50)
                checked_order_count = 0

                for page_num in paginator.page_range:
                    page_orders = paginator.page(page_num)
                    for o in page_orders.object_list:
                        orders = find_exact_match_orders(cancelled_orders, list(OrderProduct.objects.filter(order_id=o['id'], type__in=[1, 2]).values_list("product_id", flat=True)))
                        if orders:
                            result = find_exact_feature_match_order(orders, o['id'])
                            if result:
                                checked_order_count+=1
                                cancelled_orders.pop(result)

                return JsonResponse({
                    'status': 200,
                    'title': f"{checked_order_count} ta belgilandi",
                })
        except IntegrityError as e:
            return JsonResponse({
                        'status': 404,
                        'title': f"Saqlash jarayonida hatolik : {e}",
                    })
    driver_id = request.GET.get("driver", None)
    driver = User.objects.get(id=driver_id)
    allowed_districts = list(driver.allow_districts.all().values_list("id", flat=True))
    warehouse_operation = WarehouseOperation.objects.filter(action='5', from_warehouse_status="1",
                                                            from_warehouse_responsible=driver,
                                                            to_warehouse_status="1").last()
    orders_id = []
    if warehouse_operation:

        orders_id = list(
            WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation=warehouse_operation).values_list("order_id",
                                                                                                          flat=True))
    orders = Order.objects.filter(id__in=orders_id, driver=driver, barcode__isnull=False).order_by("id")
    page_number = request.GET.get('page', 1)
    order_length = request.GET.get('order_length', 50)
    paginator = Paginator(orders, order_length)
    page = paginator.get_page(page_number)

    order_list = []

    for i in page.object_list:
        data = {"id":i.id, 'barcode':i.barcode, 'is_print':i.is_print,
                'customer_name':i.customer_name, 'is_there_previous_order':i.is_there_previous_order.id if i.is_there_previous_order else None,
                'customer_phone':i.customer_phone, 'customer_phone2':i.customer_phone2,
                'customer_region':i.customer_region.name if i.customer_region is not None else '',
                'customer_district':i.customer_district.name if i.customer_district is not None else '', 'customer_street':i.customer_street,
              "total_price":i.order_products_total_price_uzs}

        product_list = []
        for p in i.order_products:

            if p.type == '1':
                if p.product_variable:
                    product_list.append({"type":p.type,"product_name":p.product.name, "color":get_object_name_or_none(p.product_variable.color), "measure_item":get_object_name_or_none(p.product_variable.measure_item), 'price':p.price_uzs, 'amount':p.ordered_amount})
                else:
                    product_list.append(
                        {"type":p.type,"product_name": p.product.name, "color": '',
                         "measure_item": '', 'price': p.price_uzs,
                         'amount': p.ordered_amount})

            else:
                collection_items = [{"product_name":item.product.name,
                                     "color":get_object_name_or_none(item.product_variable.color),
                                     "measure_item":get_object_name_or_none(item.product_variable.measure_item)} for item in OrderProduct.objects.filter(main_order_product=p)]
                product_list.append(
                    {"type":p.type,"product_name": p.product.name, "color": '',
                     "measure_item": '', 'price': p.price_uzs,
                     'amount': p.ordered_amount,
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

        'cancelled_order_count':Order.objects.filter(driver=driver, cancelled_status="1", status=5, output_product__isnull=True).count(),
        'new_order_count':Order.objects.filter(customer_region_id=driver.region_id, status=1, customer_district_id__in=allowed_districts).count(),
        'checked_order_count':orders.count()


    })
