from datetime import timedelta

import dateutil
from django.utils import timezone

from order.models import Order
from user.models import User
from django.shortcuts import get_object_or_404
from cash.models import Cash
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce


class SellerData(object):
    def __init__(self, id):
        self.id = id
        self.user = get_object_or_404(User, id=id)

    @property
    def hold_seller_fee(self):
        """Beklemede olan (henüz ödeme süresi dolmamış) tutar"""
        delay_days = self.user.seller_payment_delay_days or 0
        now = timezone.now()
        deadline_date = now - timedelta(days=delay_days)
        orders = (
            Order.objects.filter(
                seller=self.user,
                total_driver_payment_status='3',
                total_driver_payment_paid_at__gt=deadline_date,  # Süresi henüz dolmamış
            )
            .aggregate(total_fee=Sum("seller_fee"))
        )
        return orders.get("total_fee") or 0

    @property
    def balance(self):
        delay_days = self.user.seller_payment_delay_days or 0
        now = timezone.now()
        # şu anki tarihten delay_days kadar önceki tarih
        deadline_date = now - timedelta(days=delay_days)
        orders = (
            Order.objects.filter(
                seller=self.user,
                status='4',
                total_driver_payment_status='3',   # ödeme tamamlanmış
                total_driver_payment_paid_at__lte=deadline_date,  # belirlenen süreden önce ödenmişse
            )
            .aggregate(total_fee=Sum("seller_fee"))
        )
        total_fee = orders.get("total_fee") or 0
        return total_fee - self.total_payment

    @property
    def processing_seller_fee(self):
        """qayta ishlashdagi sotilgan lekin to'lovi fileal tomonidan to'liq qabul qilinmagan"""
        orders = (
            Order.objects.filter(
                seller=self.user,
                status='4',   # ödeme tamamlanmış
            ).exclude(total_driver_payment_status='3')
            .aggregate(total_fee=Sum("seller_fee"))
        )
        return orders.get("total_fee") or 0

    @property
    def being_delivered_seller_fee(self):
        """Yetkazilmoqda va filealdagilar summasi"""
        orders = (
            Order.objects.filter(
                seller=self.user,
                status__in=[13, 3]
            )
            .aggregate(total_fee=Sum("seller_fee"))
        )
        return orders.get("total_fee") or 0

    @property
    def cancelled_product_price_in_driver(self):
        """Bekor qilingan haydovchi qo'lida yoki filealdagilar summasi"""
        orders = (
            Order.objects.filter(
                seller=self.user,
                status=5
            )
            .aggregate(total_price=Sum("total_product_price"))
        )
        return orders.get("total_price") or 0

    @property
    def cancelled_product_price_in_branch(self):
        """Bekor qilingan haydovchi qo'lida yoki filealdagilar summasi"""
        orders = (
            Order.objects.filter(
                seller=self.user,
                status=14
            )
            .aggregate(total_price=Sum("total_product_price"))
        )
        return orders.get("total_price") or 0


    @property
    def total_payment(self):
        total_new_pay = Cash.objects.filter(to_user_id=self.id).aggregate(t=Coalesce(Sum("amount"), 0))['t']
        return total_new_pay

    # @property
    # def this_month_payment(self):
    #     return sum(list(PaymentOperatorFee.objects.filter(user_id=self.id, created_at__year=self.today.year, created_at__month=self.today.month).values_list("amount", flat=True)))
    @property
    def this_month_payment(self):
        total_new_pay = Cash.objects.filter(to_user_id=self.id, created_at__year=self.today.year,
                                            created_at__month=self.today.month).aggregate(t=Coalesce(Sum("amount"), 0))[
            't']
        # return sum(list(PaymentOperatorFee.objects.filter(user_id=self.id, created_at__year=self.today.year, created_at__month=self.today.month).values_list("amount", flat=True)))
        return total_new_pay

    # @property
    # def one_month_ago_payment(self):
    #     after_month = self.today - dateutil.relativedelta.relativedelta(months=1)
    #     return sum(list(PaymentOperatorFee.objects.filter(user_id=self.id, created_at__year=after_month.year, created_at__month=after_month.month).values_list("amount", flat=True)))

    @property
    def one_month_ago_payment(self):
        after_month = self.today - dateutil.relativedelta.relativedelta(months=1)
        total_new_pay = Cash.objects.filter(to_user_id=self.id, created_at__year=after_month.year,
                                            created_at__month=after_month.month).aggregate(
            t=Coalesce(Sum("amount"), 0))['t']
        return total_new_pay

    @property
    def after_month_fee(self):
        # from django.utils import timezone
        # return self.order.Order.objects.filter(
        #     operator_id=self.id,
        #     status=4,
        #     created_at__year__lte=timezone.now().year,
        #     created_at__month__lt=timezone.now().month
        # ).aggregate(total_operator_fee=Sum('operator_fee'))['total_operator_fee'] or 0

        # from django.utils import timezone
        # return self.order.Order.objects.filter(
        #     operator_id=self.id,
        #     status=4
        # ).aggregate(total_operator_fee=Sum('operator_fee'))['total_operator_fee'] or 0
        from django.utils import timezone
        from datetime import datetime, timedelta

        # Bu ayın birinci gününün tarihini al
        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Belirli bir tarihten önceki siparişlerin toplam operator_fee'ini al
        return self.order.Order.objects.filter(
            operator_id=self.id,
            status=4,
            created_at__lt=first_day_of_month
        ).aggregate(total_operator_fee=Sum('operator_fee'))['total_operator_fee'] or 0

    # @property
    # def after_month_fee(self):
    #     after_month = self.today - dateutil.relativedelta.relativedelta(months=1)

    #     return sum(list(self.order.Order.objects.filter(operator_id=self.id, status=4, created_at__year__lte=after_month.year,
    #                                                     created_at__month__lte=after_month.month).values_list('operator_fee', flat=True)))

    @property
    def total_fee(self):
        return sum(
            list(self.order.Order.objects.filter(operator_id=self.id, status=4).values_list('operator_fee', flat=True)))

    @property
    def this_mont_total_fee(self):
        return sum(list(self.order.Order.objects.filter(operator_id=self.id, status=4, created_at__year=self.today.year,
                                                        created_at__month=self.today.month).values_list('operator_fee',
                                                                                                        flat=True)))

    @property
    def order(self):
        import order
        return order.models

    @property
    def order_statuses(self):
        # Status kodu → status ismi eşlemesi
        from order.models import Status
        status_map = dict(Status)
        # Her status için sayım (tek sorguda)
        qs = (
            self.order.Order.objects
            .filter(operator_id=self.id)
            .values('status')
            .annotate(count=Count('id'))
        )
        # İstenen formata dönüştür
        result = []
        for item in qs:
            status_code = item['status']
            status_name = status_map.get(status_code, 'Nomaʼlum')  # bilinmeyen kod varsa fallback
            result.append({
                'status_name': status_name,  # senin örneğine uygun küçük harf
                'count': item['count']
            })

        return result

    @property
    def order_status(self):
        get = self.get_order_amount
        return {"send_products": get(2), 'being_delivered': get(3), 'delivered': get(4), 'canceled': get(5),
                'call_back': get(6), 'wait': get(1), 'delete': get(0)}

    def get_order_amount(self, order_status_id):
        total = self.order.Order.objects.filter(operator_id=self.id, status=str(order_status_id)).count()
        return total

    @property
    def input_order_from_date(self):
        data = []
        for count in range(10):
            day = self.today - timedelta(days=count)
            total = self.order.Order.objects.filter(operator_id=self.id, created_at__date=day).count()
            data.append({"date": str(day), 'result': total})
        return data

    def input_order_from_date_amount(self, value):
        day = self.today - timedelta(days=value)
        total = self.order.Order.objects.filter(operator_id=self.id, created_at=day).count()
        # print(day.strftime())
        return total

    @property
    def total_order_amount(self):
        order = self.order.Order.objects.filter(operator_id=self.id).count()
        return int(order)

    @property
    def order_amount_today(self):
        order = self.order.Order.objects.filter(operator_id=self.id, created_at__year=self.today.year,
                                                created_at__month=self.today.month,
                                                created_at__day=self.today.day).exclude(status__in=[9, 10, 11,12, 0]).count()
        return int(order)

    @property
    def operator_daily_limit(self):
        return 60

    @property
    def order_amount_one_month_ago(self):
        d2 = self.today - dateutil.relativedelta.relativedelta(months=1)
        order = self.order.Order.objects.filter(operator_id=self.id, created_at__year=d2.year,
                                                created_at__month=d2.month).count()
        return int(order)

    @property
    def order_amount_this_month(self):
        order = self.order.Order.objects.filter(operator_id=self.id, created_at__year=self.today.year,
                                                created_at__month=self.today.month).count()
        return int(order)

    @property
    def today(self):
        import datetime
        return datetime.date.today()
