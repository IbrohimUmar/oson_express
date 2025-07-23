import json

import dateutil
from django.db.models import Q, ExpressionWrapper, DecimalField
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from report.models import DailyReport
from user.models import User
from store.models import Product
from django.db.models import Q
import datetime
from calendar import monthrange
from django.http import JsonResponse

from .make_report import *
def get_last_day_of_month(year, month):
    _, last_day = monthrange(year, month)
    return last_day
from django.db import transaction, IntegrityError

# def make_monthly_report(year, month):
#     last_day_month = get_last_day_of_month(year, month)
#     for i in range(1, last_day_month+1):
#         date = datetime.datetime(year, month, i)
#         report = DailyReport.objects.create(date=date)
#         report_id = report.id

#         update_report_order_amount_and_price(year, month, i, report_id)
#         update_report_cash_amount(year, month, i, report_id)
#         update_drivers_debt(year, month, i, report_id)
#         update_product_price_driver_and_store(year, month, i, report_id)
#         update_shopkeeper_debts(year, month, i, report_id)
#         update_main_balance(report_id)

import logging

developer_logger = logging.getLogger('developer_logger')


def json_default(value):
    from datetime import date, datetime
    if isinstance(value, (date, datetime)):
        return value.isoformat()


import json
@login_required(login_url='/login')
@permission_required('admin.report', login_url="/home")
def report_month_by_details(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        if 'date' in body and 'type' in body:
            from datetime import datetime
            date_object = datetime.strptime(body['date'], '%Y-%m-%d')
            last_day_month = get_last_day_of_month(date_object.year, date_object.month)
            month_name = '-' + date_object.strftime('%b')
            month_len = [str(i)+month_name for i in range(1, last_day_month + 1)]
            print(month_len)
            if body['type'] == "orderDetails":
                name = "Buyurtmalar tarixi"
                r = {
                    "total_received_orders":[], "total_sold_order_quantity":[], 'total_cancelled_order_quantity':[],
                     "total_shipped_order_quantity":[], "total_sold_order_price":[], "total_cancelled_order_price":[],
                    "total_shipped_order_price":[]
                     }
                for i in range(1, last_day_month+1):
                    print(i)
                    report = DailyReport.objects.filter(date__year=date_object.year, date__month=date_object.month, date__day=i, is_main=True).first()
                    if report:
                        # r['total_shipped_order_price'].append(report.total_shipped_order_price)
                        r['total_received_orders'].append(report.total_received_orders)
                        r['total_sold_order_quantity'].append(report.total_sold_order_quantity)
                        r['total_cancelled_order_quantity'].append(report.total_cancelled_order_quantity)
                        r['total_shipped_order_quantity'].append(report.total_shipped_order_quantity)
                        r['total_sold_order_price'].append(report.total_sold_order_price)
                        r['total_cancelled_order_price'].append(report.total_cancelled_order_price)
                        r['total_shipped_order_price'].append(report.total_shipped_order_price)
                d = [
                    {"name": 'Kelgan buyurtmalar soni', 'data': r['total_received_orders']},
                    {"name": 'Sotilgan buyurtmalar soni', 'data': r['total_sold_order_quantity']},
                    {"name": 'Sotilgan buyurtmalar summasi', 'data': r['total_sold_order_price']},
                    {"name": 'Bekor qilingan buyurtmalar soni', 'data': r['total_cancelled_order_quantity']},
                    {"name": 'Bekor qilingan buyurtmalar summasi', 'data': r['total_cancelled_order_price']},

                    {"name": 'Mahsuloti yuborilgan buyurtma soni', 'data': r['total_shipped_order_quantity']},
                    {"name": 'Mahsuloti yuborilgan buyurtma summasi', 'data': r['total_shipped_order_price']},
                ]
                print(r)
                return JsonResponse({'status': 200, 'messages': "success", 'month_list':month_len,'name':name,'data':d})
            elif body['type'] == "productPriceDetails":
                name = "Tovar summasi bo'yicha"
                d = [
                    {"name": 'Ombordagi', 'data': []},
                    {"name": 'Haydovchilardagi', 'data': []}
                ]
                reports = DailyReport.objects.filter(
                    date__year=date_object.year,
                    date__month=date_object.month,
                    date__day__range=(1, last_day_month),
                    is_main=True
                ).values(
                    "total_product_price_in_warehouse",
                    "total_product_price_in_drivers",
                )
                for report in reports:
                    d[0]['data'].append(report["total_product_price_in_warehouse"])
                    d[1]['data'].append(report["total_product_price_in_drivers"])
                return JsonResponse(
                    {'status': 200, 'messages': "success", 'month_list': month_len, 'name': name, 'data': d})
            elif body['type'] == "debtDetails":
                name="Qarzdorlik bo'yicha"
                d = [
                    {"name": 'Ta\'minotchilardan qarzimiz', 'data': []},
                    {"name": 'Haydovchilarning bizdan qarzi', 'data': []}
                ]
                reports = DailyReport.objects.filter(
                    date__year=date_object.year,
                    date__month=date_object.month,
                    date__day__range=(1, last_day_month),
                    is_main=True
                ).values(
                    "drivers_debts",
                    "total_debt",
                )
                for report in reports:
                    d[0]['data'].append(report["total_debt"])
                    d[1]['data'].append(report["drivers_debts"])
                return JsonResponse(
                    {'status': 200, 'messages': "success", 'month_list': month_len, 'name': name, 'data': d})
            elif body['type'] == "inDetails":
                name="Kirim summalar bo'yicha"
                data = {}
                cash_in = CashCategory.objects.filter(cash__created_at__year=date_object.year , cash__type=1).annotate(count=Count("cash")).filter(count__gt=0)
                for i in range(1, last_day_month+1):
                    for c in cash_in:
                        cash_amount = 0
                        query_result = cash_in.filter(cash__created_at__year=date_object.year, cash__created_at__month=date_object.month, cash__created_at__day=i, id=c.id).aggregate(t=Coalesce(Sum("cash__amount"), 0))['t']
                        if query_result != 0:
                            cash_amount = query_result
                        dict_data = data.get(c.id, None)
                        if dict_data:
                            dict_data['data'].append(cash_amount)
                        else:
                            data[c.id] = {'name':c.name, 'data':[cash_amount]}
                    query_result = Cash.objects.filter(category=None,created_at__date=datetime(date_object.year, date_object.month, i),
                                                  type=1).aggregate(t=Coalesce(Sum("amount"), 0))['t']
                    dict_data = data.get(0, None)
                    if dict_data:
                        dict_data['data'].append(query_result)
                    else:
                        data[0] = {'name': "Kategoriya tanlanmagan", 'data': [query_result]}
                return JsonResponse(
                    {'status': 200, 'messages': "success", 'month_list': month_len, 'name': name, 'data': list(data.values())})
            elif body['type'] == "outDetails":
                name = "Chiqim summalar bo'yicha"

                data = {}
                cash_in = CashCategory.objects.filter(cash__created_at__year=date_object.year, cash__type=2).annotate(
                    count=Count("cash")).filter(count__gt=0)
                for i in range(1, last_day_month + 1):

                    for c in cash_in:
                        cash_amount = 0
                        query_result = cash_in.filter(cash__created_at__year=date_object.year,
                                                      cash__created_at__month=date_object.month,
                                                      cash__created_at__day=i, id=c.id).aggregate(
                            t=Coalesce(Sum("cash__amount"), 0))['t']
                        if query_result != 0:
                            cash_amount = query_result

                        dict_data = data.get(c.id, None)
                        if dict_data:
                            dict_data['data'].append(cash_amount)
                        else:
                            data[c.id] = {'name': c.name, 'data': [cash_amount]}

                    query_result = Cash.objects.filter(category=None,
                                                       created_at__date=datetime(date_object.year, date_object.month,
                                                                                 i),
                                                       type=2).aggregate(t=Coalesce(Sum("amount"), 0))['t']
                    dict_data = data.get(0, None)
                    if dict_data:
                        dict_data['data'].append(query_result)
                    else:
                        data[0] = {'name': "Kategoriya tanlanmagan", 'data': [query_result]}
                return JsonResponse(
                    {'status': 200, 'messages': "success", 'month_list': month_len, 'name': name,
                     'data': list(data.values())})
            elif body['type'] == "cashBalance":
                name="Qoldiq"
                d = [
                    {"name": 'Kun boshidagi', 'data': []},
                    {"name": 'Sof pul oqimi	', 'data': []},
                    {"name": 'Kun oxiridagi qoldiq', 'data': []},
                ]
                for i in range(1, last_day_month+1):
                    start_day_balance = 0
                    report = DailyReport.objects.filter(date__year=date_object.year, date__month=date_object.month,
                                                        date__day=i, is_main=True).first()
                    if 1 == 1:
                        from datetime import datetime, timedelta
                        date = datetime(date_object.year, date_object.month, i)
                        previous_date = date - timedelta(days=1)
                        query = DailyReport.objects.filter(date__year=previous_date.year, date__month=previous_date.month,
                                                        date__day=previous_date.day, is_main=True).first()
                        if query:
                            start_day_balance = query.total_cash_balance
                    # else:
                    #     start_day_balance = report.total_cash_balance
                    d[0]['data'].append(start_day_balance)
                    d[1]['data'].append(report.total_cash_balance - start_day_balance)
                    d[2]['data'].append(report.total_cash_balance)
                return JsonResponse(
                    {'status': 200, 'messages': "success", 'month_list': month_len, 'name': name, 'data': d})
                    
                    
            elif body['type'] == "mainBalance":
                name = "Katta balans"
                d = [
                    {"name": 'Haydovchilar qarzi', 'data': []},
                    {"name": "Haydovchilar qo'lidagi mahsulot", 'data': []},

                    {"name": "Yo'ldagi mahsulotlar summasi", 'data': []},

                    {"name": 'Ombor v2 dagi mahsulotlar summasi', 'data': []},
                    {"name": 'Hamma kassadagi jami summa', 'data': []},

                    {"name": "Xodimlardan qarzimiz", 'data': [], 'result': []},
                    {"name": "Adminlardan qarzimiz", 'data': [], 'result': []},

                    {"name": "Ta'minotchilardan qarzimiz", 'data': []},
                    {"name": 'Katta Balans', 'data': []},
                    {"date": []},

                ]
                reports = DailyReport.objects.filter(
                    date__year=date_object.year,
                    date__month=date_object.month,
                    date__day__range=(1, last_day_month),
                    is_main=True
                ).values(
                    "main_balance",
                    "employee_debt",
                    "seller_debt",

                    "total_product_price_in_warehouse",
                    "total_product_price_in_drivers",
                    "drivers_debts",
                    "total_debt",
                    "total_cash_balance",
                    "total_product_price_in_transition",
                ).order_by('date')
                for report in reports:
                    d[0]['data'].append(report["drivers_debts"])
                    d[1]['data'].append(report["total_product_price_in_drivers"])

                    d[2]['data'].append(report["total_product_price_in_transition"])

                    d[3]['data'].append(report["total_product_price_in_warehouse"])
                    d[4]['data'].append(report["total_cash_balance"])

                    d[5]['data'].append(report["employee_debt"])
                    d[6]['data'].append(report["seller_debt"])
                    d[7]['data'].append(report["total_debt"])
                    d[8]['data'].append(report["main_balance"])

                return JsonResponse(
                    {'status': 200, 'messages': "success", 'month_list': month_len, 'name': name, 'data': d})
        return JsonResponse({'status': 404, 'messages': "Ma'lumotlarda kamchilik bor"})

    return JsonResponse({'status': 404, 'messages': "Faqat post metodi qabul qilinadi"})




from config.connection.send_developer import send_private_message_developer


def create_daily_report(request):
  from datetime import date, datetime
  today = date.today()
#   yesterday = today - timedelta(days=1)
  
#   yesterday = today
  yesterday = datetime.now()
  
  send_private_message_developer(f"Kunlik hisobot saqlanmoqda saqlaniyotgan vaqt {today} - 1 kun ayrib {yesterday}")
  try:
      with transaction.atomic():
          
        DailyReport.objects.filter(date=yesterday).delete()
  
        report, create = DailyReport.objects.get_or_create(date=yesterday)
        report_id = report.id
        
        update_product_price_in_transfer(report_id)
        update_seller_debt(report_id)
        update_employee_debt(report_id)
        update_product_input_price_in_driver(report_id)
        update_product_input_price_in_transfer(report_id)
        update_product_input_price_in_warehouse(report_id)
        
        update_report_order_amount_and_price(yesterday.year, yesterday.month, yesterday.day, report_id)
        update_report_cash_amount(yesterday.year, yesterday.month, yesterday.day, report_id)
        update_drivers_debt(yesterday.year, yesterday.month, yesterday.day, report_id)
        # update_product_price_driver_and_store(yesterday.year, yesterday.month, yesterday.day, report_id)
        update_shopkeeper_debts(yesterday.year, yesterday.month, yesterday.day, report_id)
        update_main_balance(report_id)
        return JsonResponse({'status': 200, 'messages': "success"})
  except IntegrityError as e:
    developer_logger.error(e)
    return JsonResponse({'status': 500, 'messages': "error", 'message':str(e)})
  
  
  
#   except Exception as e:
#     developer_logger.error(e)
#     return JsonResponse({'status': 500, 'messages': "error", 'message':str(e)})


@login_required(login_url='/login')
@permission_required('admin.report', login_url="/home")
def report(request):
    # from django.db.models import Max
    # from datetime import date, timedelta
    # DailyReport.objects.all().delete()
    # make_monthly_report(2023, 1)
    # make_monthly_report(2024, 2)
    # make_monthly_report(2023, 3)
    # make_monthly_report(2023, 4)
    # make_monthly_report(2023, 5)
    # make_monthly_report(2023, 6)
    # make_monthly_report(2023, 7)
    # make_monthly_report(2023, 8)
    # make_monthly_report(2023, 9)
    # make_monthly_report(2023, 10)
    # make_monthly_report(2023, 11)
    # make_monthly_report(2023, 12)
    
    
    year = datetime.datetime.now().year
    if request.GET.get("year", None):
        year = request.GET['year']
    data = []
    for month in range(1,13):
        queryset = DailyReport.objects.filter(date__year=year, date__month=month,is_main=True).order_by('date').values().last()
        old_month = DailyReport.objects.filter(date__year=year, date__month=month-1,is_main=True).order_by('date').values("total_cash_balance").last()
        if queryset:
            balance_beginning_month = 0
            if old_month:
                balance_beginning_month = old_month['total_cash_balance']
            queryset['total_cash_balance_beginning_month']=balance_beginning_month
            queryset['month_cash_flow']=queryset['total_cash_balance']-balance_beginning_month

            query = DailyReport.objects.filter(date__year=year, date__month=month, is_main=True).order_by('date').aggregate(
                total_received_count=Coalesce(Sum("total_received_orders"), 0),
                total_sold_count=Coalesce(Sum("total_sold_order_quantity"), 0),
                total_cancelled_count=Coalesce(Sum("total_cancelled_order_quantity"), 0),
                total_shipped_count=Coalesce(Sum("total_shipped_order_quantity"), 0),

                total_sold_price=Coalesce(Sum("total_sold_order_price"), 0),
                total_cancelled_price=Coalesce(Sum("total_cancelled_order_price"), 0),
                total_shipped_price=Coalesce(Sum("total_shipped_order_price"), 0),
            )
            marge_dict = {**queryset, **query}
            data.append(marge_dict)


    json_data = json.dumps(data, default=json_default)
    return render(request, 'report/report.html', {'data':json_data, "cash_in":get_cash_in_history(year),
                                                  "cash_out":get_cash_out_history(year),
                                                 "year":str(year), 
                                                  })



# @login_required(login_url='/login')
# @permission_required('admin.report', login_url="/home")
# def report(request):
#     fee = get_total_fee()
#     seller_fee = get_seller_fee()
#     expenses_statistic = get_expenses_statistic()
#     total_statistic = get_total_order_statistic()
#     site_statistic = [site_statistic_orders('Mahsulot', 1), site_statistic_orders('Airshop', 2),site_statistic_orders('Savdo24', 3),site_statistic_orders('Gobazar24', 4)]
#     return render(request, 'report/report.html', {
#         "fee":fee,
#         "get_fee_order":get_fee_order(),
#         "get_product_total_price":get_product_total_price(),
#         "get_driver_statistic":get_driver_statistic(),
#         "expenses_statistic":expenses_statistic, "seller_fee":seller_fee,
#         "users":User.objects.all().count(), "total_orders": Order.objects.all().count(),
#                                                "total_product":Product.objects.all().count(), "total_statistic":total_statistic, "site_statistic":site_statistic})

from datetime import date, timedelta

@login_required(login_url='/login')
@permission_required('admin.accountant', login_url="/home")
def accountant(request):
    print(get_fee_order())
    def get_result_driver_payment():
        def get_driver_payment(day):
            return 0
        total_driver_payment = 0
        result = {"total_fee": total_driver_payment,
                  'two_day': get_driver_payment(2),
                  'seven_day': get_driver_payment(7),
                  'one_month': get_driver_payment(30)}
        return result
    expenses_statistic = get_expenses_statistic()
    balance = get_result_driver_payment()['total_fee'] -expenses_statistic['total_expenses']
    return render(request, 'report/accountant.html', { 'balance':balance,"get_total_fee":get_result_driver_payment(), 'expenses_statistic':expenses_statistic})



def get_total_fee():
    def get_driver_payment(day):
        return 0
    total_driver_payment = 0
    expenses = get_expenses_statistic()
    result = {"total_fee":total_driver_payment-expenses['total_expenses'],
              'two_day':get_driver_payment(2)-expenses['two_day'], 'seven_day':get_driver_payment(7)-expenses['seven_day'],
              'one_month':get_driver_payment(30)-expenses['one_month']}
    return result


def get_driver_statistic():
    total_balance = sum([u.balance for u in User.objects.filter(type=2)])
    return {"total_driver_debt":total_balance}



def get_product_total_price():
    total_store_house_price = sum([i.total_regions_storehouse_price for i in Product.objects.all()])
    total_all_regions_driver_price = sum([i.total_all_regions_driver_price for i in Product.objects.all()])
    driver_send_product_price = sum([i.driver_send_product_price for i in Product.objects.all()])
    return {"total_store_house_price":total_store_house_price, 'total_all_regions_driver_price':total_all_regions_driver_price,
            "driver_send_product_price":driver_send_product_price,
            'total':driver_send_product_price+total_all_regions_driver_price+total_store_house_price
            }




def get_total_order_statistic():
    def get_result(status):
        return Order.objects.filter(status=status).count()
    total_statistic = [{
        "accepted":get_result(2), "being_delivered":get_result(3),"delivered":get_result(4),
        "canceled":get_result(5), "call_back":get_result(6), "wait":get_result(7),
    }][0]
    return total_statistic


def get_seller_fee():
    def get_result(site):
        return sum(list(Order.objects.filter(site=site, status=4, seller_fee__isnull=False).values_list("seller_fee", flat=True)))
    # seller_fee_total = sum([o.site.seller_fee for o in Order.objects.filter(Q(site__site=1)| Q(site__site=2),status=4, site__seller_fee__isnull=False)])
    seller_fee_total = sum(list(Order.objects.filter(Q(site=1)| Q(site=2),status=4, seller_fee__isnull=False).values_list("seller_fee", flat=True)))
    return {"seller_fee_total":seller_fee_total, "mahsulot_seller_fee":get_result(1), "airshop_seller_fee":get_result(2)}


def get_expenses_statistic():
    return {}

def site_statistic_orders(site_name, site_id):
    def get_result(site, status):
        order = sum([a.order_products_total_ordered_amount for a in Order.objects.filter(site=site, status=status)])
        return order
    return {
        'site':site_name,
        "send_products": get_result(site_id, 2),
        "being_delivered": get_result(site_id, 3),
        "delivered": get_result(site_id, 4),
        "canceled": get_result(site_id, 5),
        "call_back": get_result(site_id, 6),
        "wait": get_result(site_id, 7),
    }

from order.models import OrderProduct, Order
def get_fee_order():
    product = sum([a.price -(a.amount * a.input_price) for a in OrderProduct.objects.filter(order__status=4)])
    marked_driver_fee = sum([a.driver_bonus_amount_won for a in Order.objects.filter(status=4)])
    order_driver_fee = sum([a.driver_fee + a.driver_bonus_amount_won for a in Order.objects.filter(status=4)])
    seller_fee = sum([a.seller_fee for a in Order.objects.filter(Q(site=2),status=4) if a.seller_fee is not None])
    result = {"total_fee_marked":product-marked_driver_fee-seller_fee, 'total_fee_real':product-order_driver_fee-seller_fee}
    return result