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
        delivery_product_amount = sum(list(order.models.OrderProduct.objects.filter(order__status=4, driver_id=self.id).values_list("total_price", flat=True)))
        return int(delivery_product_amount)


    @property
    def debt_uzs(self):
        return format_money(self.debt)


    @property
    def fee_uzs(self):
        return format_money(self.fee)

    @property
    def fee(self):
        total_driver_fee = sum(list(order.models.Order.objects.filter(driver_id=self.id, status=4).values_list("driver_fee", flat=True)))
        total_driver_bonus = sum(list(order.models.Order.objects.filter(driver_id=self.id, status=4, driver_is_bonus=True, driver_bonus_amount_won__isnull=False).values_list("driver_bonus_amount_won", flat=True)))
        if total_driver_fee:
            return int(total_driver_fee) + int(total_driver_bonus)
        return 0

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
            send_products=Count('id', filter=Q(status=2)),
            being_delivered=Count('id', filter=Q(status=3)),
            delivered=Count('id', filter=Q(status=4)),

            canceled_driver=Count('id', filter=Q(status=5, cancelled_status='1')),
            canceled_returned=Count('id', filter=Q(status=5, cancelled_status="3")),
            canceled_given_other_order=Count('id', filter=Q(status=5,cancelled_status="2")),

            call_back=Count('id', filter=Q(status=6)),
            wait=Count('id', filter=Q(status=1)),
            delete=Count('id', filter=Q(status=0))
        )
        return order_status_dict

    @property
    def order_product_by(self):
        order_status_dict = OrderProduct.objects.filter(driver_id=self.id, order__driver_id=self.id).aggregate(
            send_product=Coalesce(Sum("total_price", filter=Q(order__status=2, order__cancelled_status=1)), 0),
            cancelled_driver=Coalesce(Sum("total_price", filter=Q(order__status=5, order__cancelled_status=1)), 0),
            being_delivered=Coalesce(Sum("total_price", filter=Q(order__status=3,order__cancelled_status=1)), 0),
            call_back=Coalesce(Sum("total_price", filter=Q(order__status=6,order__cancelled_status=1)), 0),
            total=Coalesce(Sum("total_price", filter=~Q(order__status__in=[4, 2]) & Q(order__cancelled_status=1)), 0),
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



    def get_sold_precentega(self, date):
        order_status_dict = Order.objects.filter(driver_id=self.id, updated_at__date=date).aggregate(
            delivered=Count('id', filter=Q(status=4)),
            canceled=Count('id', filter=Q(status=5)),
            total=Count('id', filter=Q(status__in=[4, 5])),
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
