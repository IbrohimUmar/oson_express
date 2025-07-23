from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import get_object_or_404, render, redirect
import datetime
import calendar
from order.models import Order, OrderProduct
from django.db import models
from datetime import datetime
from django.db.models.functions import Coalesce
from user.models import User, Districts

import json


def calculate_sales_percentage(sold_orders, total_orders):
    if total_orders == 0:
        return 0  # If there are no orders, the sales percentage is 0
    else:
        sales_percentage = (sold_orders / total_orders) * 100
        # return sales_percentage
        return "{:.1f}".format(sales_percentage)


@login_required(login_url='/login')
@permission_required('admin.driver_daily_report', login_url="/home")
def driver_daily_report(request):
    drivers = []
    for d in User.objects.filter(is_active=True, type=2):
        drivers.append({"id":d.id, 'first_name':d.first_name, 'last_name':d.last_name, 'region_id':d.region_id, 'allow_districts':list(d.allow_districts.all().values_list("id", flat=True))})
    
    
    driver = None
    district = None

    if request.GET.get("driver", "0") != "0":
        driver = request.GET.get("driver", "0")
    if request.GET.get("district", "0") != "0":
        district = request.GET.get("district", "0")

    def get_result(year, month, day):
        date = datetime(year, month, day)
        order = None
        if driver:
            if district:
                order = Order.objects.filter(driver=driver, customer_district_id=district)
            else:
                order = Order.objects.filter(driver=driver)
        else:
            order = Order.objects
        order = order.aggregate(
            total_sell_count=models.Count("id",filter=models.Q(status=4, updated_at__date=date)),
            total_cancelled_count=models.Count("id", filter=models.Q(status=5, updated_at__date=date)),
            total_send_products_count=models.Count("id", filter=models.Q(driver_shipping_start_date=date)),
            total_being_delivery_count=models.Count("id", filter=models.Q(status=3,updated_at__date=date))
        )
        
        order['sold_percentage'] = calculate_sales_percentage(order['total_sell_count'], order['total_sell_count'] + order['total_cancelled_count'])
        
        
        return order
    year, month = datetime.now().year, datetime.now().month
    if request.GET.get("to", None):
        year = int(request.GET['to'][:4])
        month = int(request.GET['to'][5:])
    days = []
    sold_orders_count = []
    canceled_orders_count = []
    send_product_orders_count = []
    being_delivery_count = []

    # today = datetime.now()
    last_day_month = list(calendar.monthrange(year, month))[1] + 1
    data = []
    for i in range(1, last_day_month):
        days.append(f'{i} {datetime(year, month, i).strftime("%b")}')
        result = get_result(year, month, i)
        sold_orders_count.append(result['total_sell_count'])
        canceled_orders_count.append(result['total_cancelled_count'])
        send_product_orders_count.append(result['total_send_products_count'])
        being_delivery_count.append(result['total_being_delivery_count'])
        data.append({
            'date': datetime(year, month, i), 'report': result
        })
        

    total_sell = sum([d['report']['total_sell_count'] for d in data])
    total_cancelled = sum([d['report']['total_cancelled_count'] for d in data])
    total_send_products = sum([d['report']['total_send_products_count'] for d in data])
    total_being_delivery = sum([d['report']['total_being_delivery_count'] for d in data])      
    
    total_sold_percentage =  calculate_sales_percentage(total_sell, total_sell+total_cancelled)

    return render(request, "driver/daily_report/list.html", {"drivers":json.dumps(list(drivers)),"data":data, "dates":datetime(year, month, 1).strftime(("%Y-%m")),
                                                             'month_name':datetime(year, month, 1).strftime('%b'),
                                                             'sold_orders_count':sold_orders_count,
                                                             'send_product_orders_count':send_product_orders_count,
                                                             'being_delivery_count':being_delivery_count,
                                                             'days':days,
                                                             'canceled_orders_count':canceled_orders_count,
                                                                     'districts':json.dumps(list(Districts.objects.all().values("id", "name", "region_id"))),

                                                             'total_sell':total_sell,
                                                             'total_cancelled':total_cancelled,
                                                             'total_send_products':total_send_products,
                                                             'total_being_delivery':total_being_delivery,
                                                             'total_sold_percentage':total_sold_percentage
    })








from django.db.models import Sum, ExpressionWrapper, fields, F


@login_required(login_url='/login')
@permission_required('admin.driver_daily_report', login_url="/home")
def driver_daily_report_by_price(request):
    drivers = User.objects.filter(is_active=True, type=2).values("id","first_name", "last_name")
    driver = None
    if request.GET.get("driver", "0") != "0":
        driver = request.GET.get("driver", "0")
    def get_result(year, month, day):
        date = datetime(year, month, day)
        order_product = None
        order = Order.objects.filter(status=4, updated_at__date=date)
        if driver:
            order = order.filter(driver=driver)
            order_product = OrderProduct.objects.filter(driver=driver)
        else:
            order_product = OrderProduct.objects
        driver_fee = order.aggregate(
            total=Coalesce(Sum(
                ExpressionWrapper(
                    Coalesce(F('driver_fee'), 0) + Coalesce(F('driver_bonus_amount_won'), 0),
                    output_field=fields.IntegerField()
                )
            ), 0)
        )['total']
        # driver_fee = order.aggregate(t=Coalesce(Sum("driver_fee"), 0),w=Coalesce(Sum("driver_bonus_amount_won"), 0))
        order_pro = order_product.aggregate(
            total_sell_price=Coalesce(
                models.Sum("price", filter=models.Q(status=4, order__status=4, order__updated_at__date=date)), 0),
            total_cancelled_price=Coalesce(
                models.Sum("price", filter=models.Q(order__status=5, order__updated_at__date=date)), 0),
            total_send_products_price=Coalesce(
                models.Sum("price", filter=models.Q(order__driver_shipping_start_date=date)), 0),
            total_being_delivery_price=Coalesce(
                models.Sum("price", filter=models.Q(order__status=3, order__updated_at__date=date)), 0),
        )
        # print(driver_fee)

        order_pro['selling_price_with_out_driver_fee'] = order_pro['total_sell_price'] - driver_fee
        order_pro['driver_fee'] = driver_fee

        return order_pro
    year, month = datetime.now().year, datetime.now().month

    if request.GET.get("to", None):
        year = int(request.GET['to'][:4])
        month = int(request.GET['to'][5:])

    days = []
    sold_orders_price = []
    canceled_orders_price = []
    send_product_orders_price = []
    being_delivery_price = []
    last_day_month = list(calendar.monthrange(year, month))[1] + 1
    data = []
    for i in range(1, last_day_month):
        days.append(f'{i} {datetime(year, month, i).strftime("%b")}')
        result = get_result(year, month, i)
        sold_orders_price.append(result['total_sell_price'])
        canceled_orders_price.append(result['total_cancelled_price'])
        send_product_orders_price.append(result['total_send_products_price'])
        being_delivery_price.append(result['total_being_delivery_price'])
        data.append({
            'date': datetime(year, month, i), 'report': result
        })

    total_sell = sum([d['report']['total_sell_price'] for d in data])
    total_selling_price_with_out_driver_fee = sum([d['report']['selling_price_with_out_driver_fee'] for d in data])
    total_selling_driver_fee = sum([d['report']['driver_fee'] for d in data])
    total_cancelled = sum([d['report']['total_cancelled_price'] for d in data])
    total_send_products = sum([d['report']['total_send_products_price'] for d in data])
    total_being_delivery = sum([d['report']['total_being_delivery_price'] for d in data])

    return render(request, "driver/daily_report/price_by.html", {"drivers":drivers,"data":data, "dates":datetime(year, month, 1).strftime(("%Y-%m")),
                                                             'month_name':datetime(year, month, 1).strftime('%b'),
                                                             'sold_orders_price':sold_orders_price,
                                                             'send_product_orders_price':send_product_orders_price,
                                                             'being_delivery_price':being_delivery_price,
                                                             'days':days,
                                                             'canceled_orders_price':canceled_orders_price,

                                                             'total_sell':total_sell,
                                                             'total_cancelled':total_cancelled,
                                                             'total_send_products':total_send_products,
                                                             'total_being_delivery':total_being_delivery,
                                                             'total_selling_price_with_out_driver_fee':total_selling_price_with_out_driver_fee,
                                                             'total_selling_driver_fee':total_selling_driver_fee,

    })




# @login_required(login_url='/login')
# @permission_required('admin.operator_create_new_order', login_url="/home")
# def driver_daily_report_by_price(request):
#     drivers = User.objects.filter(is_active=True, type=2).values("id","first_name", "last_name")
#     driver = None
#     if request.GET.get("driver", "0") != "0":
#         driver = request.GET.get("driver", "0")
#     def get_result(year, month, day):
#         date = datetime(year, month, day)
#         order_product = None
#         if driver:
#             order_product = OrderProduct.objects.filter(driver=driver)
#         else:
#             order_product = OrderProduct.objects
#         order_pro = order_product.aggregate(
#             total_sell_price=Coalesce(
#                 models.Sum("price", filter=models.Q(status=4, order__status=4, order__updated_at__date=date)), 0),
#             total_cancelled_price=Coalesce(
#                 models.Sum("price", filter=models.Q(order__status=5, order__updated_at__date=date)), 0),
#             total_send_products_price=Coalesce(
#                 models.Sum("price", filter=models.Q(order__driver_shipping_start_date=date)), 0),
#             total_being_delivery_price=Coalesce(
#                 models.Sum("price", filter=models.Q(order__status=3, order__updated_at__date=date)), 0)
#         )
#         return order_pro
#     year, month = datetime.now().year, datetime.now().month

#     if request.GET.get("to", None):
#         year = int(request.GET['to'][:4])
#         month = int(request.GET['to'][5:])

#     days = []
#     sold_orders_price = []
#     canceled_orders_price = []
#     send_product_orders_price = []
#     being_delivery_price = []
#     last_day_month = list(calendar.monthrange(year, month))[1] + 1
#     data = []
#     for i in range(1, last_day_month):
#         days.append(f'{i} {datetime(year, month, i).strftime("%b")}')
#         result = get_result(year, month, i)
#         sold_orders_price.append(result['total_sell_price'])
#         canceled_orders_price.append(result['total_cancelled_price'])
#         send_product_orders_price.append(result['total_send_products_price'])
#         being_delivery_price.append(result['total_being_delivery_price'])
#         data.append({
#             'date': datetime(year, month, i), 'report': result
#         })

#     total_sell = sum([d['report']['total_sell_price'] for d in data])
#     total_cancelled = sum([d['report']['total_cancelled_price'] for d in data])
#     total_send_products = sum([d['report']['total_send_products_price'] for d in data])
#     total_being_delivery = sum([d['report']['total_being_delivery_price'] for d in data])

#     return render(request, "driver/daily_report/price_by.html", {"drivers":drivers,"data":data, "dates":datetime(year, month, 1).strftime(("%Y-%m")),
#                                                              'month_name':datetime(year, month, 1).strftime('%b'),
#                                                              'sold_orders_price':sold_orders_price,
#                                                              'send_product_orders_price':send_product_orders_price,
#                                                              'being_delivery_price':being_delivery_price,
#                                                              'days':days,
#                                                              'canceled_orders_price':canceled_orders_price,

#                                                              'total_sell':total_sell,
#                                                              'total_cancelled':total_cancelled,
#                                                              'total_send_products':total_send_products,
#                                                              'total_being_delivery':total_being_delivery,
        
#     })

