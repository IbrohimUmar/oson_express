from django.db import models
from user.models import *
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
import order
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
from tinymce.models import HTMLField


class Measure(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Nomi")
    short_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Nomi")

    def __str__(self):
        return self.name

    def items_name(self):
        return [i.name for i in MeasureItem.objects.filter(measure_id=self.id)]

    class Meta:
        verbose_name_plural = "Mahsulotlar uchun o'lchovlar"


class MeasureItem(models.Model):
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE, related_name='feature_items')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Colors(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Nomi")
    color = models.CharField(max_length=100, default='#000000', null=False, blank=False, verbose_name="Rang")

    def color_box(self):
        from django.utils.html import format_html

        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {};"></div>',
            self.color,
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Ranglar'



class Category(models.Model):
    name = models.CharField(max_length=250, null=False, verbose_name='Kategoria nomi')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Mahsulotlar kategoriyalari'




class Product(models.Model):
    bonus_type_choices = (
        ("0", "Chegirma mavjud emas"),
        ("1", "2+1 shaklidagi chegirma"),
        ("2", "2 chisidan mahsulotdan 30 000 mingdan chegirma")
    )
    APPROVAL_CHOICES = [
        ('1', 'Tasdiqlash kutilmoqda'),
        ('2', 'Tasdiqlandi'),
        ('3', 'Bekor qilindi'),
    ]
    SIZE_CHOICES = [
        ('1', "Standart o'lchovda"),
        ('2', "Gabariti katta mahsulot"),
    ]

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='1'
    )
    approval_status_updated_at = models.DateTimeField(null=True, blank=True)
    approval_status_updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                          related_name='approval_status_updated_by_user')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="seller_product",null=True, blank=True)
    name = models.CharField(max_length=350, null=True, blank=True, verbose_name="Mahsulot nomi")
    short = models.TextField(null=True, blank=True, verbose_name="Mahsulot haqida qisqacha")
    desc = HTMLField(verbose_name='Konkurs haqida to\'liq')

    seller_fee = models.IntegerField(null=False, blank=False, verbose_name='admin to\'lovi', default=0)
    toll = models.BooleanField(default=False, null=False,verbose_name="Yo'l kira pullimi")
    youtube_link = models.CharField(max_length=450, null=True, blank=True, verbose_name='Youtube video link')
    sale_price = models.IntegerField(null=False, blank=False, verbose_name='Sotuv narxi', default=0)
    image = models.ImageField(upload_to='products', null=True, blank=True, verbose_name="Katta rasim (1201 x 1801)")
    small_image = models.ImageField(upload_to='products_small', null=True, blank=True, verbose_name="Kichik rasm (180 x 240)")

    is_active = models.BooleanField(default=True, null=False, verbose_name="mahsulot sotuvdami")
    is_collection = models.BooleanField(default=False, null=False, verbose_name="bu mahsulot to'plammi")
    category = models.ManyToManyField(Category, verbose_name='Kategoriyasi', related_name='category')

    size_type = models.CharField(choices=SIZE_CHOICES, max_length=10, default='1', null=False, blank=False)
    size_based_delivery_extra = models.IntegerField(null=True, blank=True, verbose_name="Gabariti katta mahsulotning yetkazish tafovuti")


    bonus_type = models.CharField(choices=bonus_type_choices, max_length=100, default=0, null=False, blank=False)
    bonus = models.IntegerField(null=True, blank=True, verbose_name="Nechtadan so'ng berilishi kerakligi")
    bonus_amount = models.IntegerField(null=True, verbose_name="nechta yoki necha pulligi")

    colors = models.ManyToManyField(Colors, blank=True)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE, null=True, blank=True)
    measure_item = models.ManyToManyField(MeasureItem, blank=True)

    def __str__(self):
        return self.name


    @property
    def total_delivery_price(self):
        if self.size_type == '1':
            return self.seller.special_fee_amount
        elif self.size_type == '2':
            return self.seller.special_fee_amount + self.size_based_delivery_extra

    @property
    def get_sale_discount_type_title(self):
        if self.bonus_type == '1':
            return f"{self.bonus} ta olsa {self.bonus_amount} ta sovg'a"
        elif self.bonus_type == '2':
            return f"{self.bonus} chisidankeyin harbiri uchun {self.bonus_amount} so'mdan chegirma"
        return ''



    @property
    def defective_data(self):
        return DefectiveProducts(self.id)

    def total_region_amount(self, id):
        result = self.total_regions_storehouse_amount + self.total_regions_driver_amount(id)
        if result:
            return result
        return 0


    @property
    def defective_product_amount(self):
        return sum(list(
            order.models.OrderProduct.objects.filter(product_id=self.id, status=7).values_list('amount', flat=True)))

    @property
    def return_product_amount(self):
        return \
            order.models.OrderProduct.objects.filter(product_id=self.id, status=5).aggregate(
                t=Coalesce(Sum("amount"), 0))[
                't']

    @property
    def total_regions_storehouse_amount(self):
        return self.amount


    @property
    def total_regions_storehouse_price(self):
        result = int(self.total_regions_storehouse_amount) * int(self.price)
        return int(result)

    @property
    def total_all_regions_driver_amount(self):
        amount = order.models.OrderProduct.objects.exclude(order__status=4, status=4).filter(Q(status=4) | Q(status=6),
                                                                                             product_id=self.id).aggregate(
            t=Coalesce(Sum("amount"), 0))['t']
        return amount

    @property
    def driver_send_product_price(self):
        return 0


    def total_regions_wait_products(self, id):
        driver_product = sum(list(order.models.OrderProduct.objects.filter(order__status=1, product_id=self.id,
                                                                           driver__region_id=id).values_list(
            "ordered_amount", flat=True)))
        if driver_product:
            return driver_product
        return 0

    @property
    def total_wait_products(self):
        driver_product = sum(list(
            order.models.OrderProduct.objects.filter(order__status=1, product_id=self.id).values_list("ordered_amount",
                                                                                                      flat=True)))
        if driver_product:
            return driver_product
        return 0

    @property
    def need_to_buy(self):
        result = int(self.total_wait_products) - int(self.total_regions_storehouse_amount)
        if result > 0:
            return int(result)
        return 0

    class Meta:
        verbose_name_plural = 'Mahsulotlar'
        ordering = ('name',)


class ProductCollectionItem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="product_collection_item", verbose_name="Mahsulot nomi")
    collection = models.ManyToManyField(Product, verbose_name="To'plamdagi mahsulotlarni tanlang")

    class Meta:
        verbose_name_plural = "Mahsulot to'plami"
        verbose_name = "Mahsulot to'plami"




class ProductApprovalNote(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='approval_notes')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_notes_written')
    note = models.TextField(verbose_name="Izoh / Sabab")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.username if self.user else 'Anonim'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"




class ProductVariable(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variables')
    measure_item = models.ForeignKey(MeasureItem, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(Colors, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField(default=0, null=False, blank=False)
    is_first = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, null=False, verbose_name="mahsulot sotuvdami")
    is_different_price = models.BooleanField(default=False, verbose_name="Saytdagi narxdan farqlimi?")

    # bonus_exists = models.BooleanField(default=False, null=False, verbose_name="mahsulotga bonus bormi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name

    @property
    def get_color_name(self):
        if self.color:
            return self.color.name
        return ''

    @property
    def get_measure_item_name(self):
        if self.measure_item:
            return self.measure_item.name
        return ''

    @property
    def last_input_price(self):
        from warehouse.models import WarehouseOperationItemDetails
        details = WarehouseOperationItemDetails.objects.filter(product_variable_id=self.id, warehouse_operation__action="2").last()
        if details:
            return int(details.input_price)
        else:
            return 0




class ProductVariantImages(models.Model):
    product_variable = models.ForeignKey(ProductVariable, on_delete=models.CASCADE, related_name='image')
    default_image = models.ImageField(upload_to='products', null=True, blank=True, verbose_name="Rasm")
    high_image = models.ImageField(upload_to='products', null=True, blank=True,
                                   verbose_name="Rasim razmeri - width : 1201, height : 1801")
    low_image = models.ImageField(upload_to='products', null=True, blank=True,
                                  verbose_name="Rasim razmeri - width : 288, height : 431")
    video = models.FileField(upload_to='products', null=True, blank=True)
    is_main = models.BooleanField(default=False, verbose_name="Asosiy rasmmi")

    class Meta:
        verbose_name_plural = "Mahsulot rasimlari"
        verbose_name = "Mahsulot rasimlari"


    def __str__(self):
        return self.product_variable.product.name

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="80"/>'.format(self.image.url))
        else:
            return ""




from django.shortcuts import get_object_or_404


class DefectiveProducts(object):
    def __init__(self, id):
        self.id = id
        self.product = get_object_or_404(Product, id=id)

    @property
    def total_amount_driver(self):
        result = self.customize_order_product_query('6')
        if result: return result
        return 0

    @property
    def total_amount_restore(self):
        result = self.customize_order_product_query('8')
        if result: return result
        return 0

    @property
    def total_amount_store(self):
        result = self.customize_order_product_query('7')
        if result: return result
        return 0

    def customize_order_product_query(self, status):
        return order.models.OrderProduct.objects.filter(status=status, product_id=self.id).aggregate(
            t=Coalesce(Sum("amount"), 0))['t']

class ProductDeliveryPrice(models.Model):
    type_choice = (
        ("0", "Yo'l kira narxi standart"),
        ("1", "Gabaritli mahsulotlar uchun qo'shib beriladi"),
        ("2", "Yo'l kira narxi shu belgilangan summadan olinsin")
    )
    type = models.CharField(choices=type_choice, default="1", max_length=100, null=False, blank=False)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=False, blank=False)
    price = models.IntegerField(null=False, blank=False, verbose_name="Yaqindagi tumanlarga qancha tafovut")
    long_distance_price = models.IntegerField(null=False, blank=False,
                                              verbose_name="Uzoqdagi tumanlarga qancha tafovut")
    price_of_two = models.IntegerField(default=0, verbose_name="2 ta mahsulot olsa qo'shimcha")
    price_of_three = models.IntegerField(default=0, verbose_name="3 ta mahsulot olsa qo'shimcha")
    price_of_four = models.IntegerField(default=0, verbose_name="4 ta mahsulot olsa qo'shimcha")
    price_of_five = models.IntegerField(default=0, verbose_name="5 ta yoki undan ko'p olsa qo'shimcha")

    class Meta:
        verbose_name_plural = 'Haydovchilarga gabariti katta maxsulotlar uchun qo\'shib beriladigan tafovut'
        verbose_name = 'Haydovchilarga gabariti katta maxsulotlar uchun qo\'shib beriladigan tafovut'

