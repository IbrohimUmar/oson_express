from django.db import models

from config.format_money import format_money
from user.models import Regions, User, Districts
from datetime import datetime, timedelta
from store.models import Product, ProductDeliveryPrice, Colors
from django.db.models import Q
from user.models import MarkedDeliveryPrice
import jsonfield
from store.models import ProductVariable
from django.db.models.functions import Coalesce
from django.db.models import Sum, ExpressionWrapper, F
from django.utils.timezone import now
from config.settings.base import TOLL_AMOUNT
from django.db.models.functions import Coalesce
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.db.models import Sum
from cash.models import Cash


class UnsentOrderData(models.Model):
    json_data = jsonfield.JSONField()
    operator = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OperatorStream(models.Model):
    stream_name = models.CharField(max_length=200, verbose_name='Xaridor ismi', null=False, blank=False)
    product_name = models.CharField(max_length=150, verbose_name='Xaridor ismi', null=False, blank=False)
    url = models.CharField(max_length=50, verbose_name='Xaridor ismi', null=False, blank=False)
    operator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# class SellerStream:
#     pass


class MarketerStream(models.Model):
    name = models.CharField(max_length=250, verbose_name='Oqim nomi', null=False)
    product = models.ForeignKey(Product, verbose_name='Mmahsulot', on_delete=models.CASCADE)
    marketer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Sotuvchi', related_name="marketer_stream")
    is_delete = models.BooleanField(default=False, null=True, blank=True)
    url = models.CharField(max_length=20, null=True, blank=True, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

# class MarketerStreamClick():
#     pass

class MarketerStreamClick(models.Model):
    marketer_stream = models.ForeignKey(MarketerStream, on_delete=models.SET_NULL, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)





Status = (
        ("0", "O'chirib yuborilgan"),

        ("9", "Yangi"),
        ("10", "Arxivlanmoqda"),
        ("11", "Arxivlandi"),
        ("12", "Double"),

        ("1", "Mahsulot kutilmoqda"),
        ("7", "Mahsulot belgilandi"),
        ("8", "Qadoqlandi"),
        ("2", "Yuborishga tayyor"),

        ("13", "Filialda"),

        ("3", "Yetkazilmoqda"),
        ("4", "Sotildi"),
        ("5", "Bekor qilindi"),
        ("6", "Qayta qo'ng'iroq"),


        ("14", "Haydovchi filealga qaytardi"),
        ("15", "Seller filealdan qaytarib oldi"),

)






class SellerOperatorStatusDesc(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, choices=Status)
    description = models.TextField()

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = "Seller holat izohi"
        verbose_name_plural = "Seller holat izohlari"




class Order(models.Model):
    CancelledStatus = (
        ("0", "Bekor qilinmagan"),
        ("1", "Mahsulotlar haydovchida"),
        # ("2", "Mahsulotini boshqa buyurtmaga belgilandi"),
        ("3", "Mahsulotini qaytib olindi"),
    )
    driver_status_choice = (
        ("0", "--------"),
        ("1", "Yetkazilmoqda"),
        ("2", "Sotildi"),
        ("3", "Bekor qilindi"),
    )
    where_come_from_select = (
        ("1", "Oqim orqali landing pagedan keldi"),
        ("2", "Oqimsiz klient uzi buyurtma berdi"),
        ("3", "Liddan api orqali keldi"),
        ("4", "Liddan tushgan elituvchidan kiritildi"),
    )
    PaymentStatus = (
        ("1", "To'lanmagan"),
        ("2", "Qisman to'langan"),
        ("3", "To'liq to'langan"),
    )

    barcode = models.BigIntegerField(null=True, db_index=True, blank=True, unique=True)
    is_print = models.BooleanField(default=False, null=True, blank=True, verbose_name="Chop etildimi")
    transaction_lock = models.BooleanField(default=False, null=True, blank=True)
    logistic_branch_id = models.IntegerField(db_index=True, null=True, blank=True)

    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='Masul')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operator')
    operator_fee = models.IntegerField(default=0, null=True, blank=True, verbose_name='operator hizmat haqqi')
    operator_comment = models.ForeignKey(SellerOperatorStatusDesc, on_delete=models.SET_NULL, null=True, blank=True)
    operator_note = models.TextField(null=True, blank=True)

    status = models.CharField(choices=Status, max_length=50, verbose_name='Holati', null=False, blank=False)
    driver_status = models.CharField(choices=driver_status_choice, max_length=50, default='0', verbose_name='Haydovchi holati', null=False, blank=False)

    customer_name = models.CharField(max_length=150, verbose_name='Xaridor ismi', null=False, blank=False)
    customer_phone = models.CharField(max_length=50, db_index=True, verbose_name='Xaridor telefon raqami', null=False,
                                      blank=False)
    customer_phone2 = models.CharField(max_length=50, verbose_name='Xaridor telefon raqami2', null=True, blank=True)
    customer_region = models.ForeignKey(Regions, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name='Viloyati')
    customer_district = models.ForeignKey(Districts, on_delete=models.SET_NULL, null=True, blank=True,
                                          verbose_name='Tumani')
    customer_street = models.TextField(null=True, blank=True, verbose_name="Ko'cha mo'ljal")

    marketer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordered_marketer')
    marketer_fee = models.IntegerField(null=True, blank=True, verbose_name='admin to\'lovi', default=0)
    marketer_stream = models.ForeignKey(MarketerStream, on_delete=models.SET_NULL, null=True, blank=True)


    seller_fee = models.IntegerField(null=True, blank=True, verbose_name='Seller fee', default=0)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordered_seller')
    seller_fee_paid = models.IntegerField(null=True, blank=True, verbose_name='seller paid fee', default=0)
    seller_fee_paid_status = models.CharField(choices=PaymentStatus, default='1', max_length=50, verbose_name="Sellerga qilingan to'lov holati", null=False, blank=False)

    where_come_from = models.CharField(choices=where_come_from_select, max_length=50, verbose_name='Qayerdan kelgan', null=True, blank=True)
    ip = models.CharField(max_length=25, null=True, blank=True)
    user_agent = models.CharField(max_length=300,null=True, blank=True)

    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="driver")
    driver_fee = models.IntegerField(default=0, null=True, blank=True, verbose_name='haydovchi hizmat haqqi')
    driver_is_bonus = models.BooleanField(default=True, null=True, blank=True,
                                          verbose_name="Haydovchi uchun bonus bormi")
    driver_one_day_bonus = models.IntegerField(null=True, blank=True,
                                               verbose_name='1 kunda yetib borsa beriladigan bonus')
    driver_two_day_bonus = models.IntegerField(null=True, blank=True,
                                               verbose_name='2 kunda yetib borsa beriladigan bonus')
    driver_bonus_amount_won = models.IntegerField(default=0, null=True, blank=True,
                                                  verbose_name='Berilgan bonus miqdori')
    delete_desc = models.TextField(null=True, blank=True, verbose_name="O'chirishi sababi")

    is_send_barcode = models.BooleanField(default=False, null=True, blank=True,
                                          verbose_name="Barcodi jo'natildimi o'zgarganmi")
    cancelled_status = models.CharField(choices=CancelledStatus, default=0, max_length=50,
                                        verbose_name='bekor qilingan buyurtma xolati', null=False, blank=False)
    is_there_previous_order = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                                related_name='previous_order')  # qaysi buyurtmadan mahsulot olib berilgani
    is_there_product = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='next_order')  # Mahsulotlarini boshqa buyurtmaga berilganmi

    logistic_fee = models.IntegerField(null=True, blank=True, verbose_name="Logistika ulushi", default=0)
    total_logistic_fee = models.IntegerField(null=True, blank=True, verbose_name="Logistika_Fee + driver_fee", default=0)
    # postage_fee = models.IntegerField(null=True, blank=True, verbose_name='Pochta narxi', default=0)

    total_product_quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='total_product_quantity jami soni')
    total_product_price = models.IntegerField(default=0, null=True, blank=True, verbose_name='total_product_price jami mahsulot summasi')
    total_product_input_price = models.IntegerField(default=0, null=True, blank=True, verbose_name='total_product_input_price jami mahsulot kirim summasi')

    defective_product_order = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='defectiveProductOrder')  # Nuqsonli buyurtma o'rniga yuborilsa
    order_date = models.DateField(null=True, blank=True, verbose_name='Buyurtma kelgan sana', default=now)
    delivered_date = models.DateField(null=True, blank=True, verbose_name='Yetkazib berish sanasi', default=now)
    driver_shipping_start_date = models.DateField(null=True, blank=True, verbose_name='Haydovchiga berilgan sana')
    driver_status_changed_at = models.DateTimeField(null=True, blank=True, verbose_name='Haydovchi statusi o\'zgargan sana')
    operator_status_changed_at = models.DateTimeField(null=True, blank=True, verbose_name='operator statusi o\'zgargan sana')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def update_driver_fee(self):
        '''
        district bo'lsa hissoblansa bo'ladi
        '''
        order = Order.objects.get(id=self.id)
        district = order.customer_district
        if district is not None:
            driver_fee_amount = district.driver_fee
        else:
            driver_fee_amount = 0
        if order.driver:
            if self.driver.fee_is_special:
                driver_fee_amount = self.driver.special_fee_amount
        order.driver_fee = driver_fee_amount
        order.save()
        return True


    def update_product_total_price(self):
        order_products = self.order_products.all()
        total_price = order_products.aggregate(t=Coalesce(Sum("total_price"), 0))['t']
        order = Order.objects.get(id=self.id)
        order.total_product_price=total_price
        order.save()
        return True

    def update_logistic_fee(self):
        '''
        total_price hissoblanganidan dan keyin
        driver fee hissoblanganidan keyin hissoblandi
        '''
        order = Order.objects.get(id=self.id)
        seller_logistic_price = order.seller.special_fee_amount
        order.total_logistic_fee = seller_logistic_price
        order.logistic_fee = seller_logistic_price - order.driver_fee
        order.save()
        return True

    def update_seller_fee(self):
        '''
        total_price hissoblanganidan dan keyin
        driver fee hissoblanganidan keyin hissoblandi
        logistic_fee hissoblanganidan keyin hissoblanadi
        '''
        order = Order.objects.get(id=self.id)
        order.seller_fee = order.total_product_price - order.total_logistic_fee
        order.save()
        return True

    def update_product_total_quantity(self):
        order_products = self.order_products.all()
        total_quantity = order_products.aggregate(t=Coalesce(Sum("total_quantity"), 0))['t']
        order = Order.objects.get(id=self.id)
        order.total_product_quantity=total_quantity
        order.save()
        return True

    def update_total_input_price(self):
        from warehouse.models import WareHouseStock
        warehouse_stock = WareHouseStock.objects.filter(order=self, status='2').aggregate(
            t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("quantity"),
                                             output_field=models.IntegerField())), 0))['t']
        print('stock', warehouse_stock)
        order = Order.objects.get(id=self.id)
        order.total_product_input_price = warehouse_stock
        order.save()
        return True

    @property
    def check_order(self):
        site = Order.objects.filter(customer_phone=self.customer_phone,
                                    customer_region=self.customer_region,
                                    created_at__year=self.created_at.year,
                                    site=self.site).exclude(Q(status=4) | Q(status=5) | Q(status=0)).count()
        if site > 1:
            return True
        return False

    @property
    def check_variable(self):
        site = OrderProduct.objects.filter(type__in=[1, 3], order_id=self.id, product_variable__isnull=True).exists()
        if site:
            return True
        return False

    @property
    def is_delivered_date_over(self):
        from datetime import timedelta
        import datetime
        if self.driver_shipping_start_date:
            three_days_ago = datetime.datetime.today() - datetime.timedelta(days=3)
            if self.driver_shipping_start_date.strftime(("%Y-%m-%d")) < three_days_ago.strftime(
                    ("%Y-%m-%d")):  # agar 3 kun katta bo'lsa start datedan
                return True
            return False
        return False

    @property
    def is_delivered_date_over_for_driver_accept_product(self):
        # driver order history
        if self.driver_shipping_start_date:
            three_day = self.driver_shipping_start_date + timedelta(days=3)
            today = datetime.today().strftime(("%Y-%m-%d"))
            if today > three_day.strftime(("%Y-%m-%d")):
                return True
            return False
        return False

    @property
    def is_order_printable(self):
        product = OrderProduct.objects.filter(order_id=self.id).count()
        if product > 4:
            return False
        return True

    @property
    def order_products(self):
        product = OrderProduct.objects.filter(product_type__in=["1", "2", 1, 2], order_id=self.id)
        return product

    @property
    def order_products_total_price(self):
        product = sum(list(
            OrderProduct.objects.filter(product_type__in=["1", "2", 1, 2], order_id=self.id).values_list("total_price", flat=True)))
        return product

    @property
    def _int_order_products_total_price(self):
        product = sum(list(
            OrderProduct.objects.filter(product_type__in=["1", "2", 1, 2], order_id=self.id).values_list("total_price", flat=True)))
        return int(product)

    @property
    def order_products_total_ordered_amount(self):
        product = sum(list(
            OrderProduct.objects.filter(product_type__in=["1", "2", 1, 2], order_id=self.id).values_list("total_quantity",
                                                                                                 flat=True)))
        return product

    @property
    def order_products_total_unit_price(self):
        return OrderProduct.objects.filter(product_type__in=["1", "2", 1, 2], order_id=self.id).aggregate(
            t=Coalesce(Sum(F('total_quantity') * F('unit_price')), 0))['t']


    @property
    def toll_exists(self):
        if self.order_products.filter(is_delivery_free=False).exists():
            from config.settings.base import TOLL_AMOUNT
            return TOLL_AMOUNT
        return 0

    @property
    def order_products_total_price_uzs(self):
        return format_money(self.order_products.aggregate(t=Coalesce(Sum("total_price"), 0))['t'])

    @property
    def send_product_relation(self):
        from warehouse.models import WarehouseOperationAndOrderRelations
        result = WarehouseOperationAndOrderRelations.objects.filter(order_id=self.id)
        return result

    @property
    def order_products_total_input_price(self):
            return self.total_product_input_price
            # return OrderProduct.objects.filter(driver__isnull=False, order_id=self.id).aggregate(
            #     t=Coalesce(Sum(F('total_quantity') * F('input_price')), 0))['t']

    @property
    def _int_order_products_total_input_price(self):
        return self.order_products_total_input_price
        # product = sum([o['input_price'] * o['ordered_amount'] for o in OrderProduct.objects.filter(type__in=["1", "2", 1, 2], order_id=self.id).values("ordered_amount", "input_price")])
        # return int(product)

    @property
    def bonus(self):
        if self.driver_is_bonus:
            today = datetime.today().strftime(("%Y-%m-%d"))
            order_today = self.driver_shipping_start_date
            if order_today:
                order_tomorrow = self.driver_shipping_start_date + timedelta(days=1)
                if today <= order_today.strftime(("%Y-%m-%d")):
                    return self.driver_one_day_bonus
                elif today == order_tomorrow.strftime(("%Y-%m-%d")):
                    return self.driver_two_day_bonus
            return 0
        return 0
        # return 2000

    # @property
    # def wait(self):
    #     if self.status == "7":
    #         if self.driver.not_shipping_product_amount_pro_id(self.order_product.product_id) >= self.site.product_amount:
    #             return True
    #         return False

    @property
    def total_seller_fee(self):
        return self.seller_fee + 2000


    @property
    def leave_fee(self):
        leave = int(self.total_product_price) - int(
            self.total_product_input_price) - self.seller_fee - self.driver_fee + self.driver_bonus_amount_won - self.operator_fee
        return leave

    # @property
    # def input_price_total(self):
    #     leave = self.order_product.input_price * self.order_product.amount
    #     return leave

    @property
    def operator_fee_standard(self):
        return 5500






class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    status = models.CharField(choices=Status, max_length=50, verbose_name='Holati', null=False, blank=False)
    message = models.TextField()
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    json_data = jsonfield.JSONField()
    modul_name = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma izohlari"
        verbose_name_plural = "Buyurtma izohlari"



class OrderComment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    reply = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma izohlari"
        verbose_name_plural = "Buyurtma izohlari"




# class CustomStatusDesc(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     status = models.CharField(max_length=50, choices=Status)
#     description = models.TextField()
#
#     def __str__(self):
#         return self.status
#
#     class Meta:
#         verbose_name = "Holat izohi"
#         verbose_name_plural = "Holat izohlari"




class DefectiveOrderDriverFee(models.Model):
    defective_sold_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='defective_order_driver_fee_sold_order')
    exchange_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='defective_order_driver_fee_exchange_order')
    driver_fee = models.IntegerField(default=0, null=True, blank=True, verbose_name='haydovchi hizmat haqqi')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderProduct(models.Model):
    Type_choice = (
        ("1", "Donali mahsulot"),
        ("2", "Mahsulotlar to'plami"),
        ("3", "To'plam mahsuloti"),
    )
    product_type = models.CharField(choices=Type_choice, default="1", max_length=50, verbose_name='Mahsulot turi', null=False, blank=False)
    main_order_product = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='collection',
                                           verbose_name="to'plam")  # Mahsulotlarini boshqa buyurtmaga berilganmi
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='orderproduct')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_variable = models.ForeignKey(ProductVariable, on_delete=models.SET_NULL, null=True, blank=True)

    bonus_type = models.CharField(choices=Product.bonus_type_choices, max_length=100, default=0, null=False, blank=False)
    bonus_condition = models.IntegerField(null=True, blank=True, verbose_name="Nechtadan so'ng berilishi kerakligi")
    bonus_condition_quantity = models.IntegerField(null=True, verbose_name="nechta yoki necha pulligi")

    bonus_from_quantity = models.IntegerField(null=True, blank=True, verbose_name="bonus sonda qo'shilgan bo'lsa maslan 2+1 bonus bo'lsa qancha amountga qo'shilganligi")
    bonus_from_price = models.IntegerField(null=True, blank=True, verbose_name="bonus uchun narxidan tushulgan bo'lsa qancha tushulganini aniqlash uchun")

    quantity = models.IntegerField(null=True, blank=True,verbose_name="Faqat buyurtma qilingan mahsulot soni (bonuslarni qo'shmaganda) ", default=0)
    total_quantity = models.IntegerField(null=True, blank=True,verbose_name="jami mahsulotlar soni (mahsulot_soni + bonuslarni soni) ", default=0)

    unit_price = models.IntegerField(null=True, blank=True, verbose_name='Buyurtma qilingandagi dona narxi', default=0)
    total_unit_price = models.IntegerField(null=True, blank=True, verbose_name='Buyurtma qilingandagi dona narxi jami', default=0)
    total_price = models.IntegerField(null=True, blank=True, verbose_name='Mahsulot jami narxi unit price + delivery_cost - bonus amount', default=0)

    is_delivery_free = models.BooleanField(default=False, verbose_name="Yo'l kira tekinmi")
    delivery_cost = models.PositiveIntegerField(default=0,
                                                verbose_name="Yo'l kira shu mahsulotdan hissoblangan bo'lsa yo'l kira miqdori qancha")

    total_input_price = models.IntegerField(null=True, blank=True, verbose_name='Mahsulot jami kirish narxi', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def calculate_total_price(self):
        bonus_amount = 0
        if self.bonus_type == '2':
            bonus_amount = self.bonus_from_price
        order_product = OrderProduct.objects.get(id=self.id)
        order_product.total_price = (self.total_unit_price + self.delivery_cost) - bonus_amount
        order_product.save()
        return True

    def calculate_total_unit_price(self):
        order_product = OrderProduct.objects.get(id=self.id)
        order_product.total_unit_price = self.unit_price * self.quantity
        order_product.save()
        return True

    @property
    def price_uzs(self):
        return format_money(self.total_price)

    @property
    def collection_items(self):
        return OrderProduct.objects.filter(main_order_product_id=self.id)


