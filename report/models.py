from datetime import datetime
from django.db import models

from user.models import CashCategory, User

from config.format_money import format_money
from django.db.models.functions import Coalesce
from django.db.models import Sum
from cash.models import Cash


# Create your models here.
class DailyReport(models.Model):
    is_main = models.BooleanField(null=False, blank=False, verbose_name="Shu kunnig asosiy hisobotimi", default=True)

    total_received_orders = models.IntegerField(null=True, blank=True, verbose_name="Jami shu kelgan buyurtmalar soni")
    total_sold_order_quantity = models.IntegerField(null=True, blank=True, verbose_name="Shu kuni sotildi")
    total_cancelled_order_quantity = models.IntegerField(null=True, blank=True, verbose_name="Shu kuni bekor qilindi")
    total_shipped_order_quantity = models.IntegerField(null=True, blank=True, verbose_name="Shu kuni tovari chiqib yetib bordi")

    total_sold_order_price = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kuni sotilgan buyurtmalar summasi")
    total_cancelled_order_price = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kuni bekor qilingan buyurtmalar summasi")
    total_shipped_order_price = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kuni yo'lga chiqgan buyurtmalar summasi")

    drivers_debts = models.BigIntegerField(null=True, blank=True, verbose_name="Haydovchilar qarzi")
    total_debt = models.BigIntegerField(null=True, blank=True, verbose_name="Jami qarzimiz taminotchilardan")
    total_product_price_in_drivers = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kundagi haydovchilardagi mahsulot summasi")
    total_product_price_in_warehouse = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kundagi ombordagi mahsulotlar summasi")
    total_product_price_in_transition = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kundagi ombordagi mahsulotlar yo'ldagi yoki ombordan omborga tranzit qilinayotgan")
    
    seller_debt = models.BigIntegerField(null=True, blank=True, verbose_name="Jami adminlardan qarzimiz")
    employee_debt = models.BigIntegerField(null=True, blank=True, verbose_name="Jami xodimlardan qarzimiz")

    total_cash_inflow = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kuni jami kirim")
    total_cash_outflow = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kuni hami chiqim")
    total_cash_transfer = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kuni hami o'tkazma")

    total_cash_balance = models.BigIntegerField(null=True, blank=True, verbose_name="Shu kuni qo'ldagi pul")

    main_balance = models.BigIntegerField(null=True, blank=True, verbose_name="Asosiy balans")

    date = models.DateField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)








class DriverReport(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="driver_report")

    debt = models.BigIntegerField(default=0, verbose_name='Qarzi')

    total_fee = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')

    total_pay = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')

    balance = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')

    order_send_product_count = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_being_delivered_count = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_delivered_count = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_call_back_count = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_cancelled_driver_count = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_cancelled_returned_count = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_cancelled_given_other_order_count = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')

    order_send_product_selling_price = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_being_delivered_selling_price = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_delivered_selling_price = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_call_back_selling_price = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_cancelled_driver_selling_price = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')
    order_driver_hand_product_price = models.BigIntegerField(default=0, verbose_name='bonusi va daromadi')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sana')

