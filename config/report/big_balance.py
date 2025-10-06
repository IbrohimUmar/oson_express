from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.shortcuts import render

from cash.models import Cash
from order.models import OrderProduct, Order
from user.models import CashierUser, User
from django.db.models import Sum, ExpressionWrapper, F
from django.db.models.functions import Coalesce

# from warehouse.models import WarehouseOperationItemDetails


@login_required(login_url='/login')
@permission_required('admin.report_big_balance', login_url="/home")
def report_big_balance(request):
    cash_services = CashReportService()
    driver_services = DriverReportService()
    supplier_services = SupplierReportService()
    warehouse_services = WarehouseReportService()
    # site_report_services = SiteReportService()
    employee_report_services = EmployeeBalanceReportService()

    employee_services = employee_report_services.total_operator_balance
    # site_services = site_report_services.get_site_balance
    total_supplier_debt = supplier_services.get_total_debt_amount
    total_driver_debt = driver_services.total_debt_amount
    total_driver_hand_product_input_price = driver_services.total_driver_hand_product_input_price
    total_warehouse_product_price_input = warehouse_services.total_product_input_price_all_warehouse
    total_cash_balances_amount = cash_services.total_balance_amount_all_cashier
    total_transit_product_price_input = warehouse_services.total_product_input_price_all_transit

    plus = (
                total_warehouse_product_price_input + total_cash_balances_amount + total_driver_debt + total_driver_hand_product_input_price + total_transit_product_price_input)
    debt = total_supplier_debt + employee_services

    # total_balance = total_suppler_balance
    # print(-7999092395 - 1133611177)
    big_balance = plus - abs(debt)

    # print(total_supplier_debt - plus, f'suppler {total_supplier_debt}')
    # big_balance = plus - abs(total_supplier_debt)
    # taminotchidan qancha qarzimiz borligi chiqadi
    # haydovchilarni qancha qarzi borligi chiqadi
    # haydovchilardagi tovar summasi chiqadi
    # kassadagi balanslaradgi jami summa chiqadi
    # omborlardagi jami tovar summasi chiqishi kerak

    return render(request, 'report/big_balance.html', {
        "employee_services": employee_services,

        # "site_services": site_services,
        "total_supplier_debt": total_supplier_debt,
        "total_driver_debt": total_driver_debt,
        "total_driver_hand_product_input_price": total_driver_hand_product_input_price,
        "total_warehouse_product_price_input": total_warehouse_product_price_input,
        "total_transit_product_price_input": total_transit_product_price_input,

        "total_driver_delivery_product_selling_price": driver_services.total_driver_delivery_product_selling_price,
        "total_driver_cancelled_order_product_input_price": driver_services.total_driver_cancelled_order_product_input_price,

        "total_cash_balances_amount": total_cash_balances_amount,
        "big_balance": big_balance
    })


class CashReportService:
    @property
    def total_balance_amount_all_cashier(self):
        return CashierUser.objects.all().aggregate(t=Coalesce(Sum("balance"), 0))['t']

    def total_balance_amount_cashier_by(self, cashier_id):
        return CashierUser.objects.filter(user_id=cashier_id).aggregate(t=Coalesce(Sum("balance"), 0))['t']


class EmployeeBalanceReportService:
    @property
    def total_operator_balance(self):
        operator = User.objects.filter(type=3, is_active=True).order_by("-id")
        total_balance = 0
        for o in operator:
            balance = o.operator_data.balance
            if balance is not None:
                total_balance += balance
        return total_balance


class SiteReportService:
    @property
    def get_site_balance(self):
        return self.get_data()

    def get_data(self):
        import requests
        sites = [
            {'mahsulot': 'https://mahsulot.com/api/user-balance/'},
            {'airshop': 'https://airshop.uz/api/user-balance/'},
            # {'savdo24': 'https://savdo24.com/api/user-balance/'},
            # {'premiumshop': 'https://premiumshop.uz/api/user-balance/'},
        ]
        data = {
            'in_progress_balance': 0,
            'balance': 0,
            'total': 0,
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PostmanRuntime/7.36.0'
        }
        for site in sites:
            site_name = list(site.keys())[0]
            response = requests.get(site[site_name], headers=headers)
            if response.status_code == 200:
                res = response.json()
                data['in_progress_balance'] += res['in_progress_balance']
                data['balance'] += res['total_balance']
                data['total'] += (res['total_balance'] + res['in_progress_balance'])
        return dict(data)


class WarehouseReportService:

    @property
    def total_product_input_price_all_warehouse(self):
        # return WarehouseOperationItemDetails.objects.filter(
        #     warehouse_stock__warehouse_id__in=[1, 2, 3, 4],
        #     leave_amount__gt=0,
        #     warehouse_operation__to_warehouse_status="2"
        # ).aggregate(
        #     t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("leave_amount"), output_field=models.IntegerField())),
        #                0))['t'] or 0
        return 0

    @property
    def total_product_input_price_all_transit(self):
        # return WarehouseOperationItemDetails.objects.filter(
        #     warehouse_operation__action__in=[1, 3],
        #     leave_amount__gt=0,
        #     warehouse_operation__from_warehouse_status__in=["1", "2"],
        #     warehouse_operation__to_warehouse_status__in=["1", "3"]
        # ).aggregate(
        #     t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("leave_amount"), output_field=models.IntegerField())),
        #                0))['t'] or 0
        return 0

    def total_product_input_price_warehouse_by(self, warehouse_id):
        # return WarehouseOperationItemDetails.objects.filter(
        #     warehouse_stock__warehouse_id=warehouse_id,
        #     leave_amount__gt=0,
        #     warehouse_operation__to_warehouse_status="2"
        # ).aggregate(
        #     t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("leave_amount"), output_field=models.IntegerField())),
        #                0))['t'] or 0
        return 0

    def total_product_input_price_all_warehouse_date_by(self, date):
        # return WarehouseOperationItemDetails.objects.filter(
        #     warehouse_stock__warehouse_id__in=[1, 2, 3, 4],
        #     leave_amount__gt=0,
        #     warehouse_operation__to_warehouse_status="2",
        #     created_at__lte=date,
        # ).aggregate(
        #     t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("leave_amount"), output_field=models.IntegerField())),
        #                0))['t'] or 0
        return 0


class DriverReportService:
    @property
    def total_debt_amount(self):
        return self.total_sold_product_price - self.total_diver_fee - self.total_payment_amount

    @property
    def total_driver_hand_product_input_price(self):
        input_price_new = Order.objects.filter(status__in=[3, 6, 5], cancelled_status="1", driver__isnull=False).aggregate(t=Coalesce(Sum('total_product_input_price'), 0))['t']
        return input_price_new

    @property
    def total_driver_delivery_product_selling_price(self):
        input_price_new = Order.objects.filter(status__in=[3, 6], cancelled_status="1", driver__isnull=False).aggregate(t=Coalesce(Sum('total_product_price'), 0))['t']
        return input_price_new
    @property
    def total_driver_cancelled_order_product_input_price(self):
        return Order.objects.filter(status=5, cancelled_status="1", driver__isnull=False).aggregate(t=Coalesce(Sum('total_product_input_price'), 0))['t']

    @property
    def total_driver_hand_product_selling_price(self):
        return Order.objects.filter(status__in=[3,5,6], cancelled_status="1", driver__isnull=False).aggregate(
            t=Coalesce(Sum('total_product_price'), 0))['t']


    @property
    def total_sold_product_price(self):
        return Order.objects.filter(status=4, driver__isnull=False).aggregate(
            t=Coalesce(Sum('total_product_price'), 0))['t']

    @property
    def total_payment_amount(self):
        cash = Cash.objects.filter(from_user__type="2").aggregate(t=Coalesce(Sum("amount"), 0))['t'] or 0
        return cash

    @property
    def total_diver_fee(self):
        fee_bonus = Order.objects.filter(status=4, driver__isnull=False, driver_is_bonus=True).aggregate(
            t=Coalesce(Sum("driver_bonus_amount_won"), 0))['t'] or 0
        fee = Order.objects.filter(status=4, driver__isnull=False).aggregate(
            t=Coalesce(Sum("driver_fee"), 0))['t'] or 0
        return fee + fee_bonus


class SupplierReportService:
    @property
    def get_all_supplier_total_special_fee_amount(self):
        return User.objects.filter(type=5, is_active=True).aggregate(
            t=Coalesce(Sum('special_fee_amount'), 0))['t'] or 0

    @property
    def get_all_supplier_total_payment_amount(self):
        return Cash.objects.filter(to_user__type=5, to_user__is_active=True, type=2, id__gt=17638).aggregate(
            # return Cash.objects.filter(to_user__type=5, type=2).aggregate(
            total_price=Coalesce(Sum("amount"), 0, output_field=models.IntegerField()))['total_price'] or 0

    @property
    def get_all_supplier_total_input_product_price(self):
        # return WarehouseOperationItemDetails.objects.filter(
        #     warehouse_operation__action="2",
        #     warehouse_operation__from_warehouse_responsible__type=5,
        #     warehouse_operation__from_warehouse_responsible__is_active=True,
        #     warehouse_operation__from_warehouse_status="2",
        #     warehouse_operation__to_warehouse_status="2",
        # ).aggregate(
        #     t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("amount"), output_field=models.IntegerField())), 0))[
        #     't'] or 0
        return 0

    @property
    def get_total_debt_amount(self):
        # return self.get_all_supplier_total_input_product_price - (self.get_all_supplier_total_payment_amount + self.get_all_supplier_total_special_fee_amount)
        return (
                    self.get_all_supplier_total_input_product_price + self.get_all_supplier_total_special_fee_amount) - self.get_all_supplier_total_payment_amount
        # return self.get_all_supplier_total_payment_amount - (self.get_all_supplier_total_input_product_price + self.get_all_supplier_total_special_fee_amount)


