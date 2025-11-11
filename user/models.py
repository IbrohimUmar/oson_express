import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
# from store.models import *
import order
import store
from django.db.models import Q
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




class CashAllowedPaymentTypes(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'{self.id} - {self.name}'


class User(AbstractUser):
    type_choice = (
        ('1', 'Admin'),
        ('2', 'Haydovchi'),
        ('3', 'Operator'),
        ('4', 'Marketolog'),
        ('5', "Ta'minotchi"),
        ('6', "Seller"),
        ('7', "Omborchi"),
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

    seller = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='seller')

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
    seller_payment_delay_days = models.PositiveIntegerField(blank=True, null=True, default=0, verbose_name="Seller to'lovni qancha kutishi kerak")

    driver_sales_delay_limit_in_days = models.IntegerField(blank=True, null=True, default=5,
                                             verbose_name="Haydovchiga tovar berish necha kunda bloklanishi")

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
        from config.seller_app.operator.query import OperatorData
        # return config.operator.query.OperatorData(self.id)
        return OperatorData(self.id)

    @property
    def supplier_data(self):
        from config.seller_app.supplier.query import SupplierData
        return SupplierData(self.id)

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
    def marketer_data(self):
        from config.seller_app.marketer.query import MarketerData
        return MarketerData(self.id)

    @property
    def seller_data(self):
        from config.seller.query import SellerData
        return SellerData(self.id)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

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


class CashCategory(models.Model):
    Type_choices = (
        ('1', "Kirim"),
        ('2', "Chiqim"),
        ('3', "O'tkazma"),
    )
    for_who_choices = (
        ('1', "Admin uchun"),
        ('2', "Seller uchun"),
    )
    type = models.CharField(max_length=50, default='1', choices=Type_choices, null=True, blank=True,
                            verbose_name='Kategoriya turini tanlang')
    name = models.CharField(max_length=120, null=True, blank=True)
    for_who = models.CharField(max_length=2, default='1', choices=for_who_choices, null=False, blank=False,
                            verbose_name='Kim uchun')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


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




class ExportedFile(models.Model):
#     uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to="exports/")  # dosyalar buraya kaydolur
    name = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exported_files")
    is_view_user = models.BooleanField(default=False, null=False, blank=False, verbose_name="Foydalanuvchi faylni ko'rdimi")
    created_at = models.DateTimeField(auto_now_add=True)
#
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"





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


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone


class SystemLog(models.Model):
    # --- 1️⃣ Aksiyon tipi (choice)
    ACTION_CHOICES = (
        ("CashierUser_UPDATE_1", "Logistika kassa | Kirim | Kirimni qabul qilgan kassir balansiga pul qo'shildi"),
        ("CashierUser_UPDATE_2", "Logistika kassa | Auto hissoblash | Kassir balansini jami hisobni boshidan hissoblandi"),


        ("Cash_CREATE_1", "Logistika kassa | Kirim | Yangi kirim yaratildi"),
        ("Cash_CREATE_3", "Logistika kassa | Chiqim | Yangi Chiqim yaratildi"),
        ("Cash_CREATE_2", "Logistika kassa | Transfer yaratish | Kassir tomonidan o'tkazma yaratildi"),

        ("Cash_EDIT_1", "Logistika kassa | Kirim o'zgartirish | Kirim kassir tomonidan o'zgartirildi"),
        ("Cash_EDIT_2", "Logistika kassa | Transferni o'zgartirish | O'tkazma kassir tomonidan o'zgartirildi"),
        ("Cash_EDIT_3", "Logistika kassa | Chiqim o'zgartirish | Chiqim kassir tomonidan o'zgartirildi"),

        ("Order_UPDATE_1", "Haydovchi | Kirim | Kirim qilishda to'lovdan buyurtmaga summa taqsimlanib to'landi ga o'zgartirildi"),
    )
    action = models.CharField(max_length=150, choices=ACTION_CHOICES)
    # action_details = models.CharField(max_length=150, choices=ACTION_CHOICES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    details = models.JSONField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)

    # --- 4️⃣ Kim yaptı, ne zaman yaptı
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)