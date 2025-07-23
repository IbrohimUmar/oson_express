from datetime import timedelta

import dateutil
from user.models import User
from django.shortcuts import get_object_or_404
from cash.models import Cash, CashPersonalPaymentCard, UserBalanceManager
from django.db.models import Sum
from django.db.models.functions import Coalesce
from order.models import Order

class SellerData(object):
    def __init__(self, id):
        self.id = id
        self.user = get_object_or_404(User, id=id)

    @property
    def hold(self):
        return self.total_delivered_order_amount

    @property
    def balance(self):
        return (self.total_sold_order_amount + self.total_bonus_confirmed) - (self.total_payment_confirmed + self.total_payment_new)


    @property
    def total_bonus_confirmed(self):
        return UserBalanceManager.objects.filter(type='2', user=self.id, status='2').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_bonus_new(self):
        return UserBalanceManager.objects.filter(type='2', user=self.id, status='1').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_bonus_cancelled(self):
        return UserBalanceManager.objects.filter(type='2', user=self.id, status='3').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_payment_confirmed(self):
        return UserBalanceManager.objects.filter(type='1', user=self.id, status='2').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_payment_new(self):
        return UserBalanceManager.objects.filter(type='1', user=self.id, status='1').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_payment_cancelled(self):
        return UserBalanceManager.objects.filter(type='1', user=self.id, status='3').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_reduce_confirmed(self):
        return UserBalanceManager.objects.filter(type='3', user=self.id, status='2').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_reduce_new(self):
        return UserBalanceManager.objects.filter(type='3', user=self.id, status='1').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_reduce_cancelled(self):
        return UserBalanceManager.objects.filter(type='3', user=self.id, status='3').aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def total_sold_order_amount(self):
        return Order.objects.filter(status='4', seller_id=self.id).aggregate(t=Coalesce(Sum("seller_fee"), 0))['t']

    @property
    def total_delivered_order_amount(self):
        return Order.objects.filter(status__in=[2, 3, 7, 8], seller_id=self.id).aggregate(t=Coalesce(Sum("seller_fee"), 0))['t']



    @property
    def today(self):
        import datetime
        return datetime.date.today()
