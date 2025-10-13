from django.db import models
from django.db.models import Sum, ExpressionWrapper, F, Count, Q
from django.db.models.functions import Coalesce

from user.models import User
from store.models import Product, ProductVariable
# Create your models here.
from config.format_money import format_money

from config.format_money import format_money
from order.models import Order



class WareHouse(models.Model):
    choice_type = (
        ("1", "Asosiy ombor"),
        ("2", "Nosoz ombor"),
        ("3", "Qoldiq to'g'irlash ombori"),
    )
    type = models.CharField(choices=choice_type, max_length=50, default=1, null=True, blank=True)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ware_house_responsible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_type_display()


    def get_user_permission(self, user):
        permission = WarehousePermission.objects.filter(user=user, warehouse_id=self.id).first()
        return permission

    def has_permission(self, user, perm_field):
        permission = WarehousePermission.objects.filter(user=user, warehouse=self).first()
        return getattr(permission, perm_field, False) if permission else False


class WarehousePermission(models.Model):
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    has_view = models.BooleanField(default=True, verbose_name="has_view")
    input_product = models.BooleanField(default=False, verbose_name="input_product")
    transit_product = models.BooleanField(default=False, verbose_name="transfer_product")
    operation_history = models.BooleanField(default=False, verbose_name="operation_history")
    order_warehouse_action_history = models.BooleanField(default=False, verbose_name="history_orders")
    operation_history_details = models.BooleanField(default=False, verbose_name="operation_history_details")
    residue = models.BooleanField(default=False, verbose_name="residue")


    class Meta:
        unique_together = ('warehouse', 'user')  # Her kullanıcı için aynı depoya birden fazla yetki eklenemez.

    def __str__(self):
        return f"{self.user} - {self.warehouse}"




class WarehouseOperation(models.Model):
    action_type = (
        ("1", "Ombordan omborga tranzit"),
        ("2", "Omborga ta'minotchidan kirim"),

        ("3", "Buyurtma uchun chiqim"),
        ("4", "Buyurtmadan omborga kirim"),
    )
    choice_status = (
        ("1", "Tasdiqlanmagan"),
        ("2", "Tasdiqlandi"),
        ("3", "Bekor qilindi"),
    )
    action = models.CharField(choices=action_type, max_length=50, default=1, null=True, blank=True)
    status = models.CharField(choices=choice_status, max_length=50, default=1, null=True, blank=True)
    status_changed_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                           related_name="warehouse_operation_status_changed_user",
                                                           verbose_name="ombor holatini o'zgartigan masul")
    status_changed_at = models.DateTimeField(null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                   related_name="warehouse_operation_seller",
                                                   verbose_name="Seller")
    supplier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                   related_name="warehouse_operation_supplier",
                                                   verbose_name="Ta'minotchi")
    from_warehouse = models.ForeignKey(WareHouse, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="from_warehouse")
    to_warehouse = models.ForeignKey(WareHouse, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="to_warehouse")
    desc = models.TextField(null=True, blank=True,  verbose_name="Izoh")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_from_warehouse_type_name(self):
        if self.from_warehouse:
            return "Ombor"
        elif self.supplier:
            return str(self.supplier.get_type_display())
        else:
            return "Nomalum"

    @property
    def relations_order_count(self):
        return len(self.relation_orders_id)
        # return WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=self.id).count()

    @property
    def get_to_warehouse_type_name(self):
        if self.to_warehouse:
            return "Ombor"
        elif self.seller:
            return str(self.seller.get_type_display())
        else:
            return "Nomalum"

    @property
    def items(self):
        return WareHouseStock.objects.filter(warehouse_operation_id=self.id)

    @property
    def item_details(self):
        pass
        # return WarehouseOperationItemDetails.objects.filter(warehouse_operation_id=self.id)

    @property
    def items_count(self):
        return self.items.count()

    @property
    def items_total_amount(self):
        return self.items.aggregate(t=Coalesce(Sum("quantity"), 0))['t']

    @property
    def items_total_input_price(self):
        return self.items.aggregate(
            t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("quantity"), output_field=models.IntegerField())), 0))['t']

    @property
    def items_total_input_price_uzs(self):
        return format_money(self.items_total_input_price)

    @property
    def items_total_selling_price(self):
        return self.items.aggregate(t=Coalesce(Sum("selling_price") * Sum("amount"), 0))['t']

    @property
    def items_total_selling_price_uzs(self):
        return format_money(self.items_total_selling_price)


    @property
    def relation_orders_id(self):
         return set(WarehouseOperationAndOrderRelations.objects.filter(warehouse_operation_id=self.id).values_list('order_id', flat=True))


    @property
    def relation_order_status_by(self):
        order_status_dict = Order.objects.filter(id__in=self.relation_orders_id).aggregate(
            send_products=Count('id', filter=Q(status=2)),
            being_delivered=Count('id', filter=Q(status=3)),
            delivered=Count('id', filter=Q(status=4)),
            call_back=Count('id', filter=Q(status=6)),

            canceled_driver=Count('id', filter=Q(status=5, cancelled_status='1')),
            canceled_returned=Count('id', filter=Q(status=5, cancelled_status="3")),
            canceled_given_other_order=Count('id', filter=Q(status=5, cancelled_status="2")),
        )
        return order_status_dict


    @property
    def relation_order_sold_percentage(self):
        order_status_dict = Order.objects.filter(id__in=self.relation_orders_id).aggregate(
            delivered=Count('id', filter=Q(status=4)),
            canceled=Count('id', filter=Q(status=5)),
            # total=Count('id', filter=Q(status__in=[4, 5])),
            total=Count('id'),
        )

        total_orders = order_status_dict['total'] or 0
        sold_orders = order_status_dict['delivered'] or 0
        sold_percentage = 0
        if total_orders > 0 and sold_orders > 0:
            sold_percentage = (sold_orders / total_orders) * 100
        return {"sold_percentage": int(sold_percentage), "details": order_status_dict}




def get_or_zero(value):
    if value:
        return value
    return 0


class OrderWarehouseAction(models.Model):
    TYPE_CHOICES = [
        ("out", "Ombordan chiqim"),
        ("return", "Omborga Kirim"),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)




class WareHouseStock(models.Model):
    choice_action_type = (
        ("1", "Omborga taminotchidan kirim qilindi"),
        ("2", "Ombordan omborga o'tkazma qilindi"),
        ("3", "Ombordan buyurtmaga berildi"),
        ("4", "Omborga buyurtmadan qaytarib olindi"),
        ("5", "Buyurtmaga belgilanganidan ortib qoldi"),
        ("6", "Ombordan omborga o'tkazma qilishda ortib qoldi"),
        ("7", "Ombordan omborga o'tkazma bekor qilindi va omborga qayta qo'shildi"),
        ("8", "Filealdan qaytarib olingan mahsulot omborga qo'shildi"),
    )
    choice_status = (
        ("0", "not_stock"),
        ("1", "in_stock"),
        ("2", "order")
    )
    status = models.CharField(choices=choice_status, max_length=50, default=1 ,null=True, blank=True)
    action_type = models.CharField(max_length=3, choices=choice_action_type, default=1, null=True, blank=True)

    warehouse = models.ForeignKey(WareHouse, on_delete=models.SET_NULL, null=True, blank=True)
    warehouse_operation = models.ForeignKey(WarehouseOperation, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False, verbose_name="Asosiy mahsulot")
    product_variable = models.ForeignKey(ProductVariable, on_delete=models.CASCADE, null=False, blank=False, verbose_name="Asosiy mahsulot")
    quantity = models.IntegerField(null=True, blank=True,  verbose_name="Mahsulot soni")
    input_price = models.IntegerField(default=0, null=False, blank=False,  verbose_name="kirim narxi")

    lot_number = models.IntegerField(null=True, blank=True,  verbose_name="Lot number")

    generic_model_name = models.CharField(max_length=100, null=True, blank=True,  verbose_name="model nomi")
    generic_model_id = models.PositiveIntegerField(null=True, blank=True,  verbose_name="model id si")

    source_stock = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def total_input_price(self):
        return self.input_price * self.quantity





class WarehouseStockAttachmentOrder(models.Model):
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE, null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_variable = models.ForeignKey(ProductVariable, on_delete=models.SET_NULL, null=True, blank=True)
    warehouse_quantity = models.IntegerField(null=True, blank=True,verbose_name="warehouse_quantity", default=0)
    attachment_amount = models.IntegerField(null=True, blank=True,verbose_name="attachment_amount", default=0)




class WarehouseOperationAndOrderRelations(models.Model):
    warehouse_operation = models.ForeignKey(WarehouseOperation, on_delete=models.CASCADE, null=False, blank=False,
                                            related_name="WarehouseOperationAndOrderRelations")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


