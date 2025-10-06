from django.db import models
from user.models import User, CashCategory


class Cash(models.Model):
    choice_person_type = (
        ("1", "Admin to'lovlari"),
        ("2", "Seller ichki to'lovlari"),
    )
    choice_type = (
        ("1", "Kassaga Kirim"),
        ("2", "Kassadan Chiqim"),
        ("3", "Kassadan kassaga"),
    )
    person_type = models.CharField(choices=choice_person_type, max_length=2, default='1', null=False, blank=False)
    type = models.CharField(choices=choice_type, max_length=40, null=False, blank=False)
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="from_user")
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="to_user")
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="responsible")
    category = models.ForeignKey(CashCategory, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    leave_amount = models.IntegerField(default=0, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)

    obj_id = models.IntegerField(null=True, blank=True)
    model_name = models.CharField(null=True, blank=True, max_length=40)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def money_format(self):
        return "{:,.0f}".format(self.amount).replace(",", " ")

    @property
    def sold_order_price(self):
        return 0

    @property
    def sold_order_input_price(self):
        return 0

    @property
    def get_cash_order_statistic(self):
        from order.models import CashOrderRelation
        cash_order_relation = CashOrderRelation.objects.filter(cash_id=self.id, amount__gt=0)
        statistic = {
            "total_operator_fee": 0,
            "total_seller_fee": 0,
            "total_order_sold_price": 0,
            "total_order_input_price": 0,
            "total_driver_fee": 0,
            "total_fee": 0,
        }

        for i in cash_order_relation:
            order = i.order
            interest = i.order_payment_interest
            if interest != 100:
                item_total_operator_fee = int((order.operator_fee_standard * interest) / 100)
                item_total_seller_fee = int((order.seller_fee * interest) / 100)
                item_total_driver_fee = int((order.driver_fee * interest) / 100)
                item_total_order_sold_price = i.amount
                item_total_order_input_price = int((order._int_order_products_total_input_price * interest) / 100)
                fee = item_total_order_sold_price - item_total_operator_fee - item_total_seller_fee - item_total_order_input_price

                statistic['total_fee'] += fee
                statistic['total_driver_fee'] += item_total_driver_fee
                statistic['total_operator_fee'] += item_total_operator_fee
                statistic['total_seller_fee'] += item_total_seller_fee
                statistic['total_order_sold_price'] += item_total_order_sold_price
                statistic['total_order_input_price'] += item_total_order_input_price
            else:
                item_total_operator_fee = order.operator_fee_standard
                item_total_seller_fee = order.seller_fee
                item_total_driver_fee = order.driver_fee
                item_total_order_sold_price = order._int_order_products_total_price
                item_total_order_input_price = order._int_order_products_total_input_price

                # foyda = sotilgan buyurtma narxi

                fee = (
                              item_total_order_sold_price - item_total_driver_fee) - item_total_operator_fee - item_total_seller_fee - item_total_order_input_price
                statistic['total_fee'] += fee
                statistic['total_driver_fee'] += item_total_driver_fee
                statistic['total_operator_fee'] += item_total_operator_fee
                statistic['total_seller_fee'] += item_total_seller_fee
                statistic['total_order_sold_price'] += item_total_order_sold_price
                statistic['total_order_input_price'] += item_total_order_input_price

        return statistic


class CashPersonalPaymentCard(models.Model):
    cash = models.OneToOneField(Cash, on_delete=models.CASCADE, null=False, blank=False)
    payment_card = models.CharField(max_length=20, null=True, blank=True)



class UserBalanceManager(models.Model):
    status_choices = (
        ('1', "Yangi"),
        ('2', "Tasdiqlandi"),
        ('3', "Bekor qilindi"),
    )
    type_choices = (
        ('1', "To'lov"),
        ('2', "Balansga qo'shish"),
        ('3', "Balansdan ayrish"),
    )
    status = models.CharField(max_length=20, choices=status_choices, default='1', null=False, blank=False, verbose_name='turi')
    type = models.CharField(max_length=20, choices=type_choices, default='1', null=False, blank=False, verbose_name='turi')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanauvchi", null=False, blank=False,related_name="user_balance_manager_user")
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Masul", null=True, blank=True, related_name="user_balance_manager_responsible")

    payment_card = models.CharField(max_length=20, null=True, blank=True)
    amount = models.IntegerField(default=0, verbose_name='Miqdori')
    cash = models.ForeignKey(Cash, on_delete=models.SET_NULL, null=True, blank=True)

    desc = models.CharField(max_length=450, null=True, blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sana')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "UserBalanceManager"

