from django.contrib.auth.models import AbstractUser
from django.db import models
# from store.models import *
import order
import store
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import Coalesce
import dateutil.relativedelta
from datetime import datetime, timedelta
from config.format_money import format_money
from tinymce.models import HTMLField


class Regions(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):  return str(self.name)

    @property
    def total_wait(self):
        count = order.models.Order.objects.filter(status=1, customer_region_id=self.id).count()
        return count

    @property
    def total_product(self):
        count = sum([o.total_region_amount(self.id) for o in store.models.Product.objects.all()])
        return count

    @property
    def total_driver_product(self):
        count = sum([o.total_hand_products for o in User.objects.filter(region_id=self.id, type=2)])
        return count


class Districts(models.Model):
    Theme = (
        ('1', 'Yaqin'),
        ('2', 'Uzoq'),
    )
    distance = models.CharField(max_length=50, default='2', choices=Theme, null=True, blank=True,
                                verbose_name='Uzoqlik darajasi')
    region = models.ForeignKey(Regions, on_delete=models.CASCADE, null=False, blank=False, verbose_name="Viloyati")
    name = models.CharField(max_length=200, null=False, blank=False, verbose_name="Tuman nomi")
    is_active = models.BooleanField(default=True, null=False, blank=True, verbose_name='Aktivmi')
    driver_fee = models.IntegerField(null=True, blank=True, verbose_name='Shu viloyat uchun haydovchi to\'lovi',
                                     default=25000)
    driver_is_bonus = models.BooleanField(default=False, null=True, blank=True,
                                          verbose_name="Haydovchi uchun bonus bormi")
    driver_one_day_bonus = models.IntegerField(null=True, blank=True,
                                               verbose_name='1 kunda yetib borsa beriladigan bonus')
    driver_two_day_bonus = models.IntegerField(null=True, blank=True,
                                               verbose_name='2 kunda yetib borsa beriladigan bonus')

    def __str__(self):  return str(self.name)

    def order_amount(self, id):
        import order
        order = order.models.Order.objects.filter(Q(status=2) | Q(status=3) | Q(status=1) | Q(status=6), driver_id=id,
                                                  site__district_id=self.id).count()
        if order:
            return int(order)
        return 0

    class Meta:
        verbose_name_plural = 'Tumanlar'
        ordering = ('-region_id',)


class TryLogin(models.Model):
    ip_address = models.CharField(max_length=80, null=True, blank=True, verbose_name="parol")
    created_at = models.DateTimeField(auto_now_add=True)


class CashCategory(models.Model):
    Type_choices = (
        ('1', "Kirim"),
        ('2', "Chiqim"),
        ('3', "O'tkazma"),
    )
    type = models.CharField(max_length=50, default='1', choices=Type_choices, null=True, blank=True,
                            verbose_name='Kategoriya turini tanlang')
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.name


class CashAllowedPaymentTypes(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'{self.id} - {self.name}'


class User(AbstractUser):
    type_choice = (
        ('1', 'Admin'),
        ('2', 'Haydovchi'),
        ('3', 'Operator'),
        ('4', 'Sotuvchi'),
        ('5', "Ta'minotchi"),
    )
    Theme = (
        ('1', 'white'),
        ('2', 'dark'),
    )
    theme = models.CharField(max_length=50, default='2', choices=Theme, null=True, blank=True,
                             verbose_name='Admin panel rangi')
    type = models.CharField(max_length=50, choices=type_choice, default='2', null=False, blank=False,
                            verbose_name='Kim')
    birthday = models.DateField(null=True, blank=True, verbose_name='Tug\'ilgin kuni')
    region = models.ForeignKey(Regions, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Viloyati')
    district = models.ForeignKey(Districts, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Tumani')
    allow_districts = models.ManyToManyField(Districts, blank=True, verbose_name='Ruxsat etilgan viloyatlar',
                                             related_name="allow_districts")
    street = models.CharField(max_length=350, null=True, blank=True, verbose_name="Ko'cha")
    # operator_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Operator tel raqami")
    operator_id = models.CharField(max_length=20, null=True, blank=True, verbose_name="Operator id si")
    password_text = models.CharField(max_length=80, null=True, blank=True, verbose_name="parol")

    my_unique_code = models.BigIntegerField(blank=True, null=True, unique=True, verbose_name='Maxsus kodi')
    tg_user_id = models.BigIntegerField(blank=True, null=True, unique=True, verbose_name='Telegram user idsi')

    cashier = models.BooleanField(blank=True, null=True, default=False, verbose_name="Bu foydalanuvchi kassirmi")
    payment_card = models.CharField(max_length=20, null=True, blank=True, verbose_name="Karta raqami")

    salary = models.IntegerField(blank=True, null=True, default=0, verbose_name='Oylik maoshi')

    photo = models.ImageField(upload_to='operators/', null=True, blank=True)

    fee_is_special = models.BooleanField(blank=True, null=True, default=False,
                                         verbose_name="Haydovchiga maxsus daromad to'anadimi")
    special_fee_amount = models.IntegerField(blank=True, null=True, default=0,
                                             verbose_name='Haydovchining maxsus daromadi')
    is_registered_my_call = models.BooleanField(default=False)
    my_call_status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def operator_data(self):
        from config.operator.query import OperatorData
        import config
        # return config.operator.query.OperatorData(self.id)
        return OperatorData(self.id)

    @property
    def shopkeeper_data(self):
        from config.shopkeeper.query import ShopKeeperData
        return ShopKeeperData(self.id)

    @property
    def storekeeper_data(self):
        # from config.storekeeper.query import StorekeeperData
        # return StorekeeperData(self.id)
        return None

    @property
    def driver_data(self):
        from config.driver.query import DriverData
        return DriverData(self.id)

    @property
    def seller_data(self):
        from config.seller.query import SellerData
        return SellerData(self.id)

    # @property
    # def debt(self):
    #     # delivery_product_amount = sum(list(order.models.Order.objects.filter(status=4, driver_id=self.id).values_list("site__product_price", flat=True)))
    #     delivery_product_amount = sum(list(
    #         order.models.OrderProduct.objects.filter(order__status=4, driver_id=self.id, status=4).values_list("price",
    #                                                                                                            flat=True)))
    #     return int(delivery_product_amount)
    #
    # @property
    # def fee(self):
    #     total_driver_fee = sum(
    #         list(order.models.Order.objects.filter(driver_id=self.id, status=4).values_list("driver_fee", flat=True)))
    #     total_driver_bonus = sum(list(
    #         order.models.Order.objects.filter(driver_id=self.id, status=4, driver_is_bonus=True,
    #                                           driver_bonus_amount_won__isnull=False).values_list(
    #             "driver_bonus_amount_won", flat=True)))
    #     if total_driver_fee:
    #         return int(total_driver_fee) + int(total_driver_bonus)
    #     return 0
    #
    # @property
    # def balance(self):
    #     result = self.debt - self.fee - self.total_payment
    #     return result
    #
    # @property
    # def balance_employee(self):
    #     type = self.type
    #     if type == '2':
    #         return self.debt - self.fee - self.total_payment
    #     elif type == '3':
    #         return self.operator_data.balance
    #     elif type == '4':
    #         return self.shopkeeper_data.balance
    #
    #     if type not in ['5', '6']:
    #         return self.total_salary_employee - self.total_payment_employee
    #     return 0
    #
    # @property
    # def balance_employee_uzs(self):
    #     return format_money(self.balance_employee)
    #
    # @property
    # def total_payment_employee(self):
    #     import cash
    #     cash = cash.models.Cash.objects.filter(to_user_id=self.id).aggregate(t=Coalesce(Sum("amount"), 0))['t']
    #     return cash
    #
    # @property
    # def total_payment_employee_uzs(self):
    #     return format_money(self.total_payment_employee)
    #
    # @property
    # def total_salary_employee(self):
    #     from report.models import EmployeeSalaryReport
    #     employee_salary_total = \
    #     EmployeeSalaryReport.objects.filter(user_id=self.id).aggregate(t=Coalesce(Sum('amount'), 0))['t']
    #     return employee_salary_total
    #
    # @property
    # def total_salary_employee_uzs(self):
    #     return format_money(self.total_salary_employee)
    #
    # @property
    # def total_cancelled_order_price(self):
    #     return sum(list(
    #         order.models.OrderProduct.objects.filter(order__driver_id=self.id, driver_id=self.id, order__status=5,
    #                                                  order__cancelled_status=1, status=4).values_list("price",
    #                                                                                                   flat=True)))
    #
    # @property
    # def total_being_delivered_order_price(self):
    #     return sum(list(
    #         order.models.OrderProduct.objects.filter(order__driver_id=self.id, driver_id=self.id, order__status=3,
    #                                                  order__cancelled_status=1, status=4).values_list("price",
    #                                                                                                   flat=True)))
    #
    # @property
    # def total_call_back_order_price(self):
    #     return sum(list(
    #         order.models.OrderProduct.objects.filter(order__driver_id=self.id, driver_id=self.id, order__status=6,
    #                                                  order__cancelled_status=1, status=4).values_list("price",
    #                                                                                                   flat=True)))
    #
    # @property
    # def total_defected_products_price(self):
    #     return order.models.OrderProduct.objects.filter(order__driver_id=self.id, driver_id=self.id, status='6'
    #                                                     ).aggregate(t=Coalesce(Sum("price"), 0))['t']
    #
    # @property
    # def total_hand_product_price(self):
    #     return sum(list(order.models.OrderProduct.objects.filter(order__driver_id=self.id, driver_id=self.id, status=4,
    #                                                              order__cancelled_status=1).exclude(
    #         Q(order__status=4) | Q(order__status=2)).values_list("price", flat=True)))
    #     # return self.total_being_delivered_order_price + self.total_cancelled_order_price + self.total_call_back_order_price
    #
    # @property
    # def total_hand_product_input_price(self):
    #     return order.models.OrderProduct.objects.filter(order__driver_id=self.id, driver_id=self.id,
    #                                                     status__in=[4, 6]).exclude(order__status__in=[4, 2]).aggregate(
    #         t=Coalesce(Sum(F('ordered_amount') * F('input_price')), 0))['t']
    #     # return self.total_being_delivered_order_price + self.total_cancelled_order_price + self.total_call_back_order_price
    #
    # @property
    # def hand_products(self):
    #     return 0
    # @property
    # def total_hand_products(self):
    #     result = self.hand_products + self.not_shipping_product_amount
    #     return result
    #
    # @property
    # def wait_product_amount(self):
    #     waited_product_amount = sum(list(
    #         order.models.OrderProduct.objects.filter(driver_id=self.id, order__status=1, status=1,
    #                                                  order__output_product__isnull=True).values("ordered_amount",
    #                                                                                             flat=True)))
    #     return waited_product_amount
    #
    # @property
    # def wait_products(self):
    #     product = [{"id": p.id, 'driver': self.id, 'name': p.name, 'amount': self.wait_product_id_amount(p.id)} for p in
    #                store.models.Product.objects.all() if self.wait_product_id_amount(p.id) > 0]
    #     if product:
    #         return product
    #     return []
    #
    # def wait_product_id_amount(self, product_id):
    #     waited_product_amount = sum(list(
    #         order.models.OrderProduct.objects.filter(driver_id=self.id, product_id=product_id, order__status=1,
    #                                                  status=1, order__output_product__isnull=True).values_list(
    #             "ordered_amount", flat=True)))
    #     return waited_product_amount
    #
    # # ----------------------not shipping
    # @property
    # def not_shipping_products(self):
    #     product = [
    #         {"id": p.id, 'driver': self.id, 'name': p.name, 'amount': self.not_shipping_product_amount_pro_id(p.id)} for
    #         p in store.models.Product.objects.all() if self.not_shipping_product_amount_pro_id(p.id) > 0]
    #     if product:
    #         return product
    #     return []
    #
    # def not_shipping_product_amount_pro_id(self, product_id):
    #     amount = sum(list(
    #         order.models.OrderProduct.objects.filter(order__status=5, order__cancelled_status=1, product_id=product_id,
    #                                                  order__driver_id=self.id, status=4).values_list("amount",
    #                                                                                                  flat=True)))
    #
    #     # delivery_product_amount = sum([i.amount for i in order.models.OrderProduct.objects.filter(driver_id=self.id,
    #     #                                                                                           product_id=product_id).exclude(Q(order__status=5) | Q(order__isnull=True))])
    #     # output_total = self.get_total_output_product(product_id)
    #     # return_total = self.get_total_return_product(product_id)
    #     # result = (int(output_total) - int(return_total)) - delivery_product_amount
    #     return int(amount)
    #
    # @property
    # def not_shipping_product_amount(self):
    #     import order
    #     amount = sum(list(order.models.OrderProduct.objects.filter(order__status=5, order__cancelled_status=1,
    #                                                                order__driver_id=self.id, status=4).values_list(
    #         "amount", flat=True)))
    #
    #     # output_total = sum(
    #     #     [i.amount for i in order.models.OutputProductItems.objects.filter(output_product__driver_id=self.id,
    #     #                                                                       output_product__is_shipping=True)])
    #     # delivery_product_amount = sum([i.amount for i in
    #     #                                order.models.OrderProduct.objects.filter(driver_id=self.id).exclude(Q(order__status=5) | Q(order__isnull=True))])
    #     # return_products = sum(list(order.models.OrderProduct.objects.filter(status=5).values_list("amount", flat=True)))
    #     # result = (int(output_total)- return_products) - delivery_product_amount
    #     return int(amount)
    #
    # def get_total_return_product(self, product_id):
    #     # return sum([i.amount for i in store.models.ReturnProductItems.objects.filter(product_id=product_id, return_product__driver_id=self.id)])
    #     return sum(list(
    #         order.models.OrderProduct.objects.filter(status=5, product_id=product_id).values_list("amount", flat=True)))
    #
    # @property
    # def order_status(self):
    #     get = self.get_order_amount
    #     return {"send_products": get(2), 'being_delivered': get(3), 'delivered': get(4), 'canceled': get(5),
    #             'call_back': get(6), 'wait': get(1), 'delete': get(0)}
    #
    # def get_order_amount(self, order_status_id):
    #     total = order.models.Order.objects.filter(driver_id=self.id, status=str(order_status_id)).count()
    #     return total
    #
    # @property
    # def delay_orders(self):
    #     import datetime
    #     today = datetime.date.today()
    #     total = order.models.Order.objects.filter(driver_id=self.id, delivered_date__lte=today).exclude(
    #         Q(status=5) | Q(status=4)).count()
    #     return total
    #
    # @property
    # def total_expenses(self):
    #     return 0
    #
    # @property
    # def total_payment(self):
    #     import cash
    #     cash = cash.models.Cash.objects.filter(from_user_id=self.id).aggregate(t=Coalesce(Sum("amount"), 0))['t']
    #     return cash
    #
    # @property
    # def total_payment_this_mont(self):
    #     import datetime
    #     import cash
    #     today = datetime.date.today()
    #     cash = cash.models.Cash.objects.filter(from_user_id=self.id, created_at__year=today.year,
    #                                            created_at__month=today.month).aggregate(t=Coalesce(Sum("amount"), 0))[
    #         't']
    #
    #
    #     # today = datetime.date.today()
    #     # total = sum([i.amount for i in DriverPayment.objects.filter(user_id=self.id, created_at__year=today.year,
    #     #                                                             created_at__month=today.month)])
    #     return cash
    #
    # @property
    # def total_expenses_this_mont(self):
    #     return 0
    #
    # @property
    # def total_expenses_one_mont_ago(self):
    #     return 0
    #
    # def product_hand_amount(self, product_id):
    #     order_pro = sum(list(order.models.OrderProduct.objects.filter(
    #         Q(order__status=3) | Q(order__status=5, order__cancelled_status=1) | Q(status=6),
    #         status=4, order__driver_id=self.id, product_id=product_id).values_list("amount", flat=True)))
    #     # result = (self.get_total_output_product(product_id) - self.get_total_return_product(product_id)) - self.get_order_status_total(4, product_id)
    #     return order_pro
    #
    # def set_pro_id_order_status_by_result_this_driver_id(self, product_id):
    #     not_shipping_pro_amount = self.not_shipping_product_amount_pro_id(product_id)
    #     query = self.get_order_status_total
    #     total_amount = self.product_hand_amount(product_id)
    #     wait = self.wait_product_id_amount(product_id)
    #     way = sum([i.amount for i in order.models.OutputProductItems.objects.filter(product_id=product_id,
    #                                                                                 output_product__driver_id=self.id,
    #                                                                                 output_product__is_shipping=False)])
    #     dict = {'total': total_amount, 'being_delivered': query(3, product_id), 'call_back': query(6, product_id),
    #             'stock': not_shipping_pro_amount, 'wait': wait, 'way': query(2, product_id)}
    #     return dict
    #
    # def get_total_output_product(self, product_id):
    #     output_total = sum([i.amount for i in
    #                         order.models.OutputProductItems.objects.filter(output_product__driver_id=self.id,
    #                                                                        product_id=product_id,
    #                                                                        output_product__is_shipping=True)])
    #     return output_total
    #
    # def get_order_status_total(self, status, product_id):
    #     return sum([o.ordered_amount for o in
    #                 order.models.OrderProduct.objects.filter(driver_id=self.id, order__status=status,
    #                                                          product_id=product_id)])
    #
    # @property
    # def order(self):
    #     import order
    #     return order.models
    #
    # @property
    # def operator_order_amount_total(self):
    #     order = self.order.Order.objects.filter(operator_id=self.id).count()
    #     return int(order)
    #
    # @property
    # def operator_order_amount_one_month_ago(self):
    #     d2 = self.today - dateutil.relativedelta.relativedelta(months=1)
    #     order = self.order.Order.objects.filter(operator_id=self.id, created_at__year=d2.year,
    #                                             created_at__month=d2.month).count()
    #     return int(order)
    #
    # @property
    # def operator_order_amount_this_month(self):
    #     order = self.order.Order.objects.filter(operator_id=self.id, created_at__year=self.today.year,
    #                                             created_at__month=self.today.month).count()
    #     return int(order)

    @property
    def today(self):
        import datetime
        return datetime.date.today()

    class Meta:
        verbose_name_plural = 'Foydalanuvchilar'


class DriverUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0, verbose_name='balansi')
    allowed_cashier = models.ManyToManyField(User, blank=True, related_name="allowed_cashier",
                                             verbose_name="Tanlashi mumkin bo'lgan kassirlar")
    updated_at = models.DateTimeField(auto_now=True)


class CashierUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0, verbose_name='balansi')
    cash_category = models.ManyToManyField(CashCategory, blank=True,
                                           verbose_name="Tanlashi mumkin bo'lgan kategoriyalar")
    cash_allowed_payment_types = models.ManyToManyField(CashAllowedPaymentTypes,
                                                        verbose_name="chiqim qilishi mumkin bo'lgan xodim turlari",
                                                        blank=True)  # to'lov qilish mumkin bo'lgan tylar
    updated_at = models.DateTimeField(auto_now=True)

class Token(models.Model):
    phone = models.IntegerField(null=False, blank=False)
    token = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)









class TempPayment(models.Model):
    status = (
        ('1', "Tasdiqlanmagan"),
        ('2', "Bekor qilindi"),
    )
    status = models.CharField(max_length=20, choices=status, default='1', null=False, blank=False, verbose_name='turi')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Daromad olgan haydovchi",
                             related_name="temp_payment_user")
    amount = models.IntegerField(default=0, verbose_name='Miqdori')
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="temp_payment_cashier")
    category = models.ForeignKey(CashCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="temp_payment_category")
    desc = models.CharField(max_length=450, null=True, blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sana')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Temp pay"


class MarkedDeliveryPrice(models.Model):
    amount = models.IntegerField(null=False, blank=False, verbose_name="Miqdori")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Oxirgi o'zgartirish sanasi")

    class Meta:
        verbose_name_plural = "Haydovchilar uchun belgilangan yo'l kira puli miqdori"


class Concourse(models.Model):
    type = (
        ('1', 'Haydovchilar uchun'),
        ('2', 'Operatorlar uchun'),
    )
    type = models.CharField(max_length=50, choices=type, default='2', null=False, blank=False, verbose_name='Kim uchun')
    name = models.CharField(max_length=500, null=False, blank=False, verbose_name='Konkurs nomi')
    photo = models.ImageField(upload_to='images/Concourse/', null=True, blank=True)
    full_desc = HTMLField(verbose_name='Konkurs haqida to\'liq')
    start_data = models.DateField(verbose_name='Boshlanish sanasi', null=False, blank=False)
    finish_data = models.DateField(verbose_name='Yakunlanish sanasi', null=False, blank=False)
    is_active = models.BooleanField(default=True, verbose_name='Konkurs activmi')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Operatorlar va haydovchilar Konkursi'
