from datetime import timedelta

import dateutil
from datetime import datetime, timedelta
from django.utils import timezone
from order.models import Order, OrderProduct
from user.models import User
from django.shortcuts import get_object_or_404
from cash.models import Cash
from django.db.models import Sum, Count, Q
from django.db.models.functions import Coalesce
import order
from config.format_money import format_money

class DriverData(object):
    def __init__(self, id):
        self.id = id
        self.user = get_object_or_404(User, id=id)


    @property
    def debt(self):
        orders = Order.objects.filter(driver_status=2, driver_id=self.id).aggregate(t=Coalesce(Sum('total_product_price'), 0))['t']
        return orders

    @property
    def debt_uzs(self):
        return format_money(self.debt)


    @property
    def fee_uzs(self):
        return format_money(self.fee)

    @property
    def fee(self):
        total_driver_fee = Order.objects.filter(driver_status=2, driver_id=self.id).aggregate(t=Coalesce(Sum('driver_fee'), 0))['t']
        return total_driver_fee

    @property
    def balance(self):
        result = self.debt - self.fee - self.total_payment
        return result

    @property
    def balance_uzs(self):
        return format_money(self.balance)




    @property
    def total_payment_uzs(self):
        return format_money(self.total_payment)

    @property
    def total_payment(self):
        import cash
        cash = cash.models.Cash.objects.filter(from_user_id=self.id).aggregate(t=Coalesce(Sum("amount"), 0))['t']
        return cash


    @property
    def order_status_by(self):
        order_status_dict = Order.objects.filter(driver_id=self.id).aggregate(
            being_delivered=Count('id', filter=Q(driver_status=1)),
            delivered=Count('id', filter=Q(driver_status=2)),

            canceled_driver=Count('id', filter=Q(driver_status=3, status=5)),
            canceled_returned=Count('id', filter=Q(driver_status=3, status__in=["14", '15'])),
            canceled_total=Count('id', filter=Q(driver_status=3)),
        )
        return order_status_dict

    @property
    def order_product_by(self):
        order_status_dict = Order.objects.filter(driver_id=self.id).aggregate(
            cancelled_driver=Coalesce(Sum("total_product_price", filter=Q(driver_status=3, status=5)), 0),
            being_delivered=Coalesce(Sum("total_product_price", filter=Q(driver_status=1)), 0),
            total=Coalesce(Sum("total_product_price", filter=Q(status__in=[3, 5])), 0)
        )
        return order_status_dict


    @property
    def order_product_by_uzs(self):
        value = self.order_product_by
        result = {}
        for i in self.order_product_by:
            result[i] = format_money(value[i])
        return result
        # return { for i in self.order_product_by}



    @property
    def delayed_order_count(self):
        from datetime import timedelta, date
        seven_days_ago = date.today() - timedelta(days=self.user.driver_sales_delay_limit_in_days)
        return Order.objects.filter(status__in=['3', '5'],  driver=self.user, driver_shipping_start_date__lt=seven_days_ago).count()


    @property
    def delayed_order_details(self):
        from datetime import timedelta, date
        seven_days_ago = date.today() - timedelta(days=self.user.driver_sales_delay_limit_in_days)
        return Order.objects.filter(status__in=['3', '5'],  driver=self.user, driver_shipping_start_date__lt=seven_days_ago).aggregate(
            beng_delivered_count=Count("id", filter=Q(status='3')),
            cancelled_count=Count("id", filter=Q(status='5'))
        )



    def get_sold_precentega(self, date):
        order_status_dict = Order.objects.filter(driver_id=self.id, driver_status_changed_at__date=date).aggregate(
            delivered=Count('id', filter=Q(driver_status=2)),
            canceled=Count('id', filter=Q(driver_status=3)),
            total=Count('id', filter=Q(status__in=[2, 3])),
        )
        total_orders = order_status_dict['total'] or 0
        sold_orders = order_status_dict['delivered'] or 0
        sold_percentage = 0
        if total_orders > 0 and sold_orders > 0:
            sold_percentage = (sold_orders / total_orders) * 100
        return {"date":date, "sold_percentage":int(sold_percentage), "details":order_status_dict}


    @property
    def three_days_sold_percentage(self):
        today = timezone.now().date()
        three_days_ago = today - timedelta(days=3)
        date_range = (three_days_ago, today)
        # Son üç günün tarihlerini içeren bir liste oluştur
        date_list = [today - timedelta(days=i) for i in range(2, -1, -1)]
        result = []
        for a in date_list:
            result.append(self.get_sold_precentega(a))
        return result

    # @property
    # def order_status_by(self):
    #     get = self.get_order_amount
    #     return {"send_products": get(2), 'being_delivered': get(3), 'delivered': get(4), 'canceled': get(5),
    #             'call_back': get(6), 'wait': get(1), 'delete':get(0)}
    #
    # def get_order_amount(self, order_status_id):
    #     total = order.models.Order.objects.filter(driver_id=self.id, status=str(order_status_id)).count()
    #     return total
