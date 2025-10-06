from django.db.models import Q, ExpressionWrapper
from report.models import DailyReport
from user.models import User, CashCategory
from order.models import Order
from django.db.models import Sum, F, Q, Count
from cash.models import Cash
from django.db.models.functions import Coalesce
import datetime
from calendar import monthrange
from django.db import models
from order.models import Order, OrderProduct
# from warehouse.models import WarehouseOperationItemDetails
from config.report.big_balance import WarehouseReportService, SupplierReportService, DriverReportService




def update_report_order_amount_and_price(year, month, day, report_id):
    date = datetime.datetime(year, month, day, 23, 59)
    order_counts = Order.objects.aggregate(
        total_received_count=models.Count("id", filter=models.Q(created_at__date=date)),
        total_sell_count=models.Count("id", filter=models.Q(status=4, updated_at__date=date)),
        total_cancelled_count=models.Count("id", filter=models.Q(status=5, updated_at__date=date)),
        total_send_products_count=models.Count("id", filter=models.Q(driver_shipping_start_date=date)),
    )
    order_pro = OrderProduct.objects.aggregate(
        total_sell_price=Coalesce(
            models.Sum("price", filter=models.Q(status=4, order__status=4, order__updated_at__date=date)), 0),
        total_cancelled_price=Coalesce(
            models.Sum("price", filter=models.Q(order__status=5, order__updated_at__date=date)), 0),
        total_send_products_price=Coalesce(
            models.Sum("price", filter=models.Q(order__driver_shipping_start_date=date)), 0),
    )
    report = DailyReport.objects.get(id=report_id)
    report.total_received_orders = order_counts['total_received_count']
    report.total_sold_order_quantity = order_counts['total_sell_count']
    report.total_cancelled_order_quantity = order_counts['total_cancelled_count']
    report.total_shipped_order_quantity = order_counts['total_send_products_count']

    report.total_sold_order_price = order_pro['total_sell_price']
    report.total_cancelled_order_price = order_pro['total_cancelled_price']
    report.total_shipped_order_price = order_pro['total_send_products_price']
    report.save()
    return True

def update_report_cash_amount(year, month, day, report_id):
    date = datetime.datetime(year, month, day, 23, 59)
    # shu yerda muammo bor hamma kirim hamma chiqimlarni oladi aslida balansdeb bitta kassirni kirim chiqimi hissoblaiyotgan edi
    cash = Cash.objects.filter(created_at__date=date).aggregate(
        total_cash_inflow=Coalesce(models.Sum("amount", filter=models.Q(type=1)), 0),
        total_cash_outflow=Coalesce(models.Sum("amount", filter=models.Q(type=2)), 0),
        total_cash_transfer=Coalesce(models.Sum("amount", filter=models.Q(type=3)), 0),
    )
    total_in = Cash.objects.filter(to_user__cashieruser__isnull=False, created_at__lte=date).aggregate(
        t=Coalesce(models.Sum("amount"), 0))['t']
    total_out = Cash.objects.filter(from_user__cashieruser__isnull=False, created_at__lte=date).aggregate(
        t=Coalesce(models.Sum("amount"), 0))['t']
    report = DailyReport.objects.get(id=report_id)
    report.total_cash_inflow = cash['total_cash_inflow']
    report.total_cash_outflow = cash['total_cash_outflow']
    report.total_cash_transfer = cash['total_cash_transfer']
    report.total_cash_balance = total_in - total_out
    report.save()
    return True




def update_product_price_in_transfer(report_id):
    warehouse_service = WarehouseReportService()
    transit_product_price = warehouse_service.total_product_input_price_all_transit
    report = DailyReport.objects.get(id=report_id)
    report.total_product_price_in_transition = transit_product_price
    report.save()


from config.report.big_balance import SiteReportService, EmployeeBalanceReportService
def update_seller_debt(report_id):
    site_report = SiteReportService()
    report = DailyReport.objects.get(id=report_id)
    report.seller_debt = site_report.get_site_balance['total']
    report.save()


def update_employee_debt(report_id):
    employee_balance_service = EmployeeBalanceReportService()
    report = DailyReport.objects.get(id=report_id)
    report.employee_debt = employee_balance_service.total_operator_balance
    report.save()


def update_product_input_price_in_driver(report_id):
    report = DailyReport.objects.get(id=report_id)
    driver_report_services = DriverReportService()
    report.total_product_price_in_drivers = driver_report_services.total_driver_hand_product_input_price
    report.save()


def update_product_input_price_in_transfer(report_id):
    report = DailyReport.objects.get(id=report_id)
    warehouse_service = WarehouseReportService()
    transit_product_price = warehouse_service.total_product_input_price_all_transit
    report.total_product_price_in_transition = transit_product_price
    report.save()

def update_product_input_price_in_warehouse(report_id):
    report = DailyReport.objects.get(id=report_id)
    warehouse_service = WarehouseReportService()
    warehouses_leave_products_input_price = warehouse_service.total_product_input_price_all_warehouse
    report.total_product_price_in_warehouse = warehouses_leave_products_input_price
    report.save()


# def update_product_price_driver_and_store(year, month, day, report_id):
#     date = datetime.datetime(year, month, day, 23, 59)
#     warehouse_service = WarehouseReportService()
#     warehouses_leave_products_input_price = warehouse_service.total_product_input_price_all_warehouse_date_by(date)
#     report = DailyReport.objects.get(id=report_id)
#     report.total_product_price_in_warehouse = warehouses_leave_products_input_price
#     report.save()


def update_shopkeeper_debts(year, month, day, report_id):
    supplier_report_service = SupplierReportService()
    report = DailyReport.objects.get(id=report_id)
    report.total_debt = supplier_report_service.get_total_debt_amount
    report.save()


def update_drivers_debt(year, month, day, report_id):
    driver_report_service = DriverReportService()
    report = DailyReport.objects.get(id=report_id)
    report.drivers_debts = driver_report_service.total_debt_amount
    report.save()


def update_main_balance(report_id):
    report = DailyReport.objects.get(id=report_id)
    plus = report.total_product_price_in_warehouse + report.total_product_price_in_transition + report.total_product_price_in_drivers + int(report.drivers_debts) + report.total_cash_balance
    debt = report.total_debt + report.seller_debt + report.employee_debt
    result = plus - abs(debt)
    report.main_balance = result
    report.save()



def get_cash_in_history(year):
    cash_in = list(CashCategory.objects.filter(cash__created_at__year=year, cash__type=1).annotate(
        jan=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=1)), 0),
        feb=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=2)), 0),
        mart=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=3)), 0),
        aprel=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=4)), 0),
        may=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=5)), 0),
        jun=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=6)), 0),
        jul=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=7)), 0),
        avg=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=8)), 0),
        sep=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=9)), 0),
        oct=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=10)), 0),
        now=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=11)), 0),
        dec=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=12)), 0),
        count=Count("cash"),
    ).filter(count__gt=0).values("id", "name", "jan", "feb", "mart", "aprel", "may", "jun", "jul", "avg", "sep", "oct",
                                 "now", "dec", "count"))

    cash_in_None_category = Cash.objects.filter(created_at__year=year, category=None, type=1).aggregate(
        jan=Coalesce(Sum("amount", filter=Q(created_at__month=1)), 0),
        feb=Coalesce(Sum("amount", filter=Q(created_at__month=2)), 0),
        mart=Coalesce(Sum("amount", filter=Q(created_at__month=3)), 0),
        aprel=Coalesce(Sum("amount", filter=Q(created_at__month=4)), 0),
        may=Coalesce(Sum("amount", filter=Q(created_at__month=5)), 0),
        jun=Coalesce(Sum("amount", filter=Q(created_at__month=6)), 0),
        jul=Coalesce(Sum("amount", filter=Q(created_at__month=7)), 0),
        avg=Coalesce(Sum("amount", filter=Q(created_at__month=8)), 0),
        sep=Coalesce(Sum("amount", filter=Q(created_at__month=9)), 0),
        oct=Coalesce(Sum("amount", filter=Q(created_at__month=10)), 0),
        now=Coalesce(Sum("amount", filter=Q(created_at__month=11)), 0),
        dec=Coalesce(Sum("amount", filter=Q(created_at__month=12)), 0),
        count=Count("id"),
    )
    cash_in.append(cash_in_None_category)
    return cash_in


def get_cash_out_history(year):
    cash_out = list(CashCategory.objects.filter(cash__created_at__year=year).annotate(
        jan=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=1, cash__type=2)), 0),
        feb=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=2, cash__type=2)), 0),
        mart=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=3, cash__type=2)), 0),
        aprel=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=4, cash__type=2)), 0),
        may=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=5, cash__type=2)), 0),
        jun=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=6, cash__type=2)), 0),
        jul=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=7, cash__type=2)), 0),
        avg=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=8, cash__type=2)), 0),
        sep=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=9, cash__type=2)), 0),
        oct=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=10, cash__type=2)), 0),
        now=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=11, cash__type=2)), 0),
        dec=Coalesce(Sum("cash__amount", filter=Q(cash__created_at__month=12, cash__type=2)), 0),
        count=Count("cash", filter=Q(cash__type=2)),
    ).filter(count__gt=0).values("id", "name", "jan", "feb", "mart", "aprel", "may", "jun", "jul", "avg", "sep", "oct",
                                 "now", "dec", "count"))
    cash_out_None_category = Cash.objects.filter(created_at__year=year, category=None, type=2).aggregate(
        jan=Coalesce(Sum("amount", filter=Q(created_at__month=1)), 0),
        feb=Coalesce(Sum("amount", filter=Q(created_at__month=2)), 0),
        mart=Coalesce(Sum("amount", filter=Q(created_at__month=3)), 0),
        aprel=Coalesce(Sum("amount", filter=Q(created_at__month=4)), 0),
        may=Coalesce(Sum("amount", filter=Q(created_at__month=5)), 0),
        jun=Coalesce(Sum("amount", filter=Q(created_at__month=6)), 0),
        jul=Coalesce(Sum("amount", filter=Q(created_at__month=7)), 0),
        avg=Coalesce(Sum("amount", filter=Q(created_at__month=8)), 0),
        sep=Coalesce(Sum("amount", filter=Q(created_at__month=9)), 0),
        oct=Coalesce(Sum("amount", filter=Q(created_at__month=10)), 0),
        now=Coalesce(Sum("amount", filter=Q(created_at__month=11)), 0),
        dec=Coalesce(Sum("amount", filter=Q(created_at__month=12)), 0),
        count=Count("id"),
    )
    cash_out.append(cash_out_None_category)
    return cash_out