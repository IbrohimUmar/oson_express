from django.db import models
from django.db.models import Sum, ExpressionWrapper, F, Count, Q
from django.db.models.functions import Coalesce

from user.models import User
from store.models import Product, ProductVariable
# Create your models here.
from config.format_money import format_money


class WareHouse(models.Model):
    choice_type = (
        ("1", "Asosiy soz ombor"),
        ("2", "Asosiy nosoz ombor"),
        ("3", "Asosiy qoldiq to'g'irlash ombori"),

        ("4", "Haydovchi bo'shdagilar ombor"),
        ("5", "Haydovchi yetkaziliyotganlar ombori"),
        ("6", "Haydovchi nosoz ombori"),
        ("7", "Haydovchi tranzit"),
    )
    type = models.CharField(choices=choice_type, max_length=50, default=1, null=True, blank=True)
    name = models.CharField(max_length=30, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ware_house_owner")
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="ware_house_responsible")
    desc = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_type_display()


class WareHousePerson(models.Model):
    person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ware_house_person")
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE, null=False, blank=False)


from config.format_money import format_money


class WareHouseStock(models.Model):
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="Asosiy mahsulot")
    product_variable = models.ForeignKey(ProductVariable, on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name="Mahsulot hususiyatlari")

    input_price = models.IntegerField(null=True, blank=True, verbose_name="kirim narxi")
    selling_price = models.IntegerField(null=True, blank=True, verbose_name="sotish narxi")

    amount = models.IntegerField(null=True, blank=True, verbose_name="Mahsulot soni")
    attachment_amount = models.IntegerField(null=True, blank=True, verbose_name="Mahsulot soni")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_warehouse_operation_item_details_queryset(self):
        return WarehouseOperationItemDetails.objects.filter(
            warehouse_stock_id=self.id,
            leave_amount__gt=0,
            warehouse_operation__to_warehouse_status="2"
        )

    @property
    def total_input_price(self):
        result = self.get_warehouse_operation_item_details_queryset.aggregate(
            t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("leave_amount"), output_field=models.IntegerField())),
                       0)
        )['t']
        return result

    @property
    def total_input_price_uzs(self):
        return format_money(self.total_input_price)

    @property
    def get_input_price_list(self):
        return self.get_warehouse_operation_item_details_queryset.values("leave_amount", "input_price")


# sokga qo'shilsa ayrilsa hammasidan qahca qo'shilib ayrilganini saqledi tarih saqlash uchun
class WareHouseStockHistory(models.Model):
    warehouse_stock = models.ForeignKey(WareHouseStock, on_delete=models.CASCADE, null=False, blank=False)
    amount = models.IntegerField(null=True, blank=True, verbose_name="Mahsulot soni")
    obj_id = models.IntegerField(null=True, blank=True, verbose_name="obyekt idsi")
    model_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="model name")
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    expired_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WarehouseOperation(models.Model):
    action_type = (
        ("1", "Ombordan omborga tranzit"),
        ("2", "Omborga ta'minotchidan kirim"),
        ("3", "Ombordan haydovchiga chiqim"),
        ("4", "Omborga haydovchidan mahsulot qaytarish"),
        ("5", "Haydovchi atkaziga baykod berish"),

    )
    choice_status = (
        ("1", "Tasdiqlanmagan"),
        ("2", "Tasdiqlandi"),
        ("3", "Bekor qilindi"),
    )
    action = models.CharField(choices=action_type, max_length=50, default=1, null=True, blank=True)

    from_warehouse = models.ForeignKey(WareHouse, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="from_warehouse_operation")
    from_warehouse_responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                   related_name="from_warehouse_operation_responsible",
                                                   verbose_name="ombor holatini o'zgartigan masul")
    from_warehouse_desc = models.CharField(max_length=500, null=True, blank=True)
    from_warehouse_status = models.CharField(choices=choice_status, max_length=50, default=1, null=True, blank=True)
    from_warehouse_status_changed_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                           related_name="from_warehouse_status_changed_user",
                                                           verbose_name="ombor holatini o'zgartigan masul")
    from_warehouse_confirm_date = models.DateTimeField(null=True, blank=True)

    to_warehouse = models.ForeignKey(WareHouse, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="to_warehouse_operation")
    to_warehouse_desc = models.CharField(max_length=500, null=True, blank=True)
    to_warehouse_status = models.CharField(choices=choice_status, max_length=50, default=1, null=True, blank=True)
    to_warehouse_status_changed_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                         related_name="to_warehouse_status_changed_user",
                                                         verbose_name="ombor holatini o'zgartigan masul")
    to_warehouse_responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                 related_name="to_warehouse_operation_responsible",
                                                 verbose_name="ombor holatini o'zgartigan masul")
    to_warehouse_confirm_date = models.DateTimeField(null=True, blank=True)

    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="warehouse_operation_reponsible")
    creating_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="warehouse_operation_creating_user")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_from_warehouse_type_name(self):
        if self.from_warehouse:
            return "Ombor"
        elif self.from_warehouse_responsible:
            return str(self.from_warehouse_responsible.get_type_display())
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
        elif self.to_warehouse_responsible:
            return str(self.to_warehouse_responsible.get_type_display())
        else:
            return "Nomalum"

    @property
    def items(self):
        return WarehouseOperationItem.objects.filter(warehouse_operation_id=self.id)

    @property
    def item_details(self):
        return WarehouseOperationItemDetails.objects.filter(warehouse_operation_id=self.id)

    @property
    def items_count(self):
        return self.items.count()

    @property
    def items_total_amount(self):
        return self.items.aggregate(t=Coalesce(Sum("amount"), 0))['t']

    @property
    def items_total_input_price(self):
        return self.item_details.aggregate(
            t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("amount"), output_field=models.IntegerField())), 0))[
            't']

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


    @property
    def relation_order_is_close(self):
        order = Order.objects.filter(id__in=self.relation_orders_id, status__in=[3, 2, 5, 6]).exclude(status=5, cancelled_status__in=['2', '3']).exists()
        if order:
            return False
        return True


def get_or_zero(value):
    if value:
        return value
    return 0


class WarehouseOperationItem(models.Model):
    warehouse_operation = models.ForeignKey(WarehouseOperation, on_delete=models.CASCADE, null=False, blank=False,
                                            related_name="WarehouseOperationItem")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mahsulot nomi")
    product_variable = models.ForeignKey(ProductVariable, on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name="Mahsulot hususiyatlari")
    warehouse_stock = models.ForeignKey(WareHouseStock, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name="Sotuvchi ombori")
    input_price = models.IntegerField(null=False, blank=False, default=0, verbose_name="kirim narxi")
    selling_price = models.IntegerField(null=False, blank=False, default=0, verbose_name="sotish narxi")
    amount = models.IntegerField(null=False, blank=False, default=0, verbose_name="Mahsulot soni")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def item_details(self):
        return WarehouseOperationItemDetails.objects.filter(warehouse_operation_item_id=self.id)

    @property
    def input_price_uzs(self):
        return format_money(self.input_price)

    @property
    def total_input_price(self):
        return self.item_details.aggregate(
            t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("amount"), output_field=models.IntegerField())), 0))[
            't']

    @property
    def total_input_price_uzs(self):
        return format_money(self.total_input_price)

        # result = get_or_zero(self.input_price) * get_or_zero(self.amount)
        # return format_money(result)

    @property
    def selling_price_uzs(self):
        return format_money(self.selling_price)

    @property
    def total_selling_price_uzs(self):
        result = get_or_zero(self.selling_price) * get_or_zero(self.amount)
        return format_money(result)


from order.models import OrderProduct, Order


# class WarehouseOperationItemTransfer(models.Model):
#     from_warehouse_operation_item = models.ForeignKey(WarehouseOperationItem, on_delete=models.CASCADE, null=False, blank=False, related_name="from_warehouse_operation_item_history")
#     to_warehouse_operation_item = models.ForeignKey(WarehouseOperationItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="to_warehouse_operation_item_history")
#     to_order_product = models.ForeignKey(OrderProduct, on_delete=models.SET_NULL, null=True, blank=True)
#     amount = models.IntegerField(null=True, blank=True,  verbose_name="Mahsulot soni")
#     leave_amount = models.IntegerField(null=True, blank=True,  verbose_name="Mahsulot soni")
#     input_price = models.IntegerField(null=True, blank=True,  verbose_name="Mahsulot kirim narxi")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#


class WarehouseOperationItemDetails(models.Model):
    from_warehouse_operation = models.ForeignKey(WarehouseOperation, on_delete=models.SET_NULL, null=True, blank=True,
                                                 related_name="WarehouseOperationItemDetailsFromOperations")
    from_warehouse_operation_item = models.ForeignKey(WarehouseOperationItem, on_delete=models.SET_NULL, null=True,
                                                      blank=True,
                                                      related_name="WarehouseOperationItemDetailsFromOperationsItem")
    from_warehouse_operation_item_details = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,
                                                              related_name="WarehouseOperationItemDetailsFromOperationsItemDetails")
    from_warehouse_stock = models.ForeignKey(WareHouseStock, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name="WarehouseOperationItemDetailsFromWarehouseStock")
    from_warehouse_input_price = models.IntegerField(null=False, blank=False, default=0,
                                                     verbose_name="dan ombor kirim narxi")
    from_order_product = models.ForeignKey(OrderProduct, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="WarehouseOperationItemDetailsFromOrderProduct")

    warehouse_operation = models.ForeignKey(WarehouseOperation, on_delete=models.CASCADE, null=False, blank=False,
                                            related_name="WarehouseOperationItemDetailsOperations")
    warehouse_operation_item = models.ForeignKey(WarehouseOperationItem, on_delete=models.CASCADE, null=False,
                                                 blank=False,
                                                 related_name="WarehouseOperationItemDetailsOperationsItem")
    warehouse_stock = models.ForeignKey(WareHouseStock, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name="Sotuvchi ombori",
                                        related_name="WarehouseOperationItemDetailsWarehouseStock")

    order_product = models.ForeignKey(OrderProduct, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="WarehouseOperationItemDetailsOrderProduct")

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mahsulot nomi")
    product_variable = models.ForeignKey(ProductVariable, on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name="Mahsulot hususiyatlari")

    input_price = models.IntegerField(null=False, blank=False, default=0, verbose_name="kirim narxi")
    amount = models.IntegerField(null=False, blank=False, default=0, verbose_name="Mahsulot soni")
    leave_amount = models.IntegerField(null=False, blank=False, default=0, verbose_name="Qolgan mahsulot soni")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def input_price_uzs(self):
        return format_money(self.input_price)


class WarehouseOperationAndOrderRelations(models.Model):
    action_type = (
        ("1", "Ombordan mahsulot yuborish"),
        ("2", "Mahsulot qaytarish"),
    )
    action = models.CharField(choices=action_type, max_length=50, default=1, null=True, blank=True)
    warehouse_operation = models.ForeignKey(WarehouseOperation, on_delete=models.CASCADE, null=False, blank=False,
                                            related_name="WarehouseOperationAndOrderRelations")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
