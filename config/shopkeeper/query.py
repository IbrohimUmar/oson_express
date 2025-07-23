
from user.models import User
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum, ExpressionWrapper
from django.db import models
from django.db.models.functions import Coalesce
from cash.models import Cash
from config.format_money import format_money
from warehouse.models import WarehouseOperationItemDetails


class ShopKeeperData(object):
    def __init__(self, id):
        self.id=id
        self.user = get_object_or_404(User, id=id)

    @property
    def balance(self):
        if self.user.is_active is True:
            return self.total_payment - (self.total_debt_products_amount + self.user.special_fee_amount)
        return 0
    @property
    def balance_format_money(self):
        return format_money(self.balance)


    @property
    def total_buy_products_amount(self):
        
        operation = WarehouseOperationItemDetails.objects.filter(
            warehouse_operation__action="2",
            warehouse_operation__from_warehouse_responsible_id=self.id,
            warehouse_operation__to_warehouse_status="2",
            # from_warehouse_operation__from_warehouse_status="2",
            warehouse_operation__from_warehouse_status="2"

        ).aggregate(t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("amount"), output_field=models.IntegerField())), 0))['t']
        return operation

    @property
    def total_buy_products_amount_format_money(self):
        return format_money(self.total_buy_products_amount)

    @property
    def total_debt_products_amount(self):
        
        # operation = WarehouseOperationItemDetails.objects.filter(
        #     from_warehouse_operation__from_warehouse_responsible_id=self.id,
        #     from_warehouse_operation__from_warehouse_status="2",
        #     from_warehouse_operation__to_warehouse_status="2",
        #                                                          ).aggregate(t=Coalesce(Sum(ExpressionWrapper(F("input_price") * F("amount"), output_field=models.IntegerField())), 0))['t']
        return self.total_buy_products_amount
        # return InputProductItems.objects.filter(input_product__shopkeeper_id=self.id, input_product__pay_type__in=[1, 2]).exclude(price__isnull=True).exclude(
        #     amount__isnull=True).aggregate(
        #     total_price=Coalesce(Sum(ExpressionWrapper(F("price") * F("amount"), output_field=models.IntegerField())), 0))['total_price']

    @property
    def total_debt_products_amount_format_money(self):
        return format_money(self.total_debt_products_amount)


    @property
    def total_payment(self):
        return Cash.objects.filter(id__gt=17638, to_user_id=self.id, type=2).aggregate(total_price=Coalesce(Sum("amount"), 0, output_field=models.IntegerField()))['total_price']

    @property
    def total_payment_format_money(self):
        return format_money(self.total_payment)





# from user.models import User
# from django.shortcuts import get_object_or_404
# from django.db.models import F, Sum, ExpressionWrapper
# from django.db import models
# from django.db.models.functions import Coalesce
# from cash.models import Cash
# from store.models import InputProductItems
# from config.format_money import format_money


# class ShopKeeperData(object):
#     def __init__(self, id):
#         self.id=id
#         self.user = get_object_or_404(User, id=id)

#     @property
#     def balance(self):
#         return self.total_payment - (self.total_debt_products_amount + self.user.special_fee_amount)

#     @property
#     def balance_format_money(self):
#         return format_money(self.balance)


#     @property
#     def total_buy_products_amount(self):
#         return InputProductItems.objects.filter(input_product__pay_type__in=[1, 2],input_product__shopkeeper_id=self.id).exclude(price__isnull=True).exclude(
#             amount__isnull=True).aggregate(total_price=Sum(ExpressionWrapper(F("price") * F("amount"), output_field=models.IntegerField())))[
#             'total_price']

#     @property
#     def total_buy_products_amount_format_money(self):
#         return format_money(self.total_buy_products_amount)

#     @property
#     def total_debt_products_amount(self):
#         return InputProductItems.objects.filter(input_product__shopkeeper_id=self.id, input_product__pay_type__in=[1, 2]).exclude(price__isnull=True).exclude(
#             amount__isnull=True).aggregate(
#             total_price=Coalesce(Sum(ExpressionWrapper(F("price") * F("amount"), output_field=models.IntegerField())), 0))['total_price']

#     @property
#     def total_debt_products_amount_format_money(self):
#         return format_money(self.total_debt_products_amount)


#     @property
#     def total_payment(self):
#         return Cash.objects.filter(to_user_id=self.id, type=2).aggregate(total_price=Coalesce(Sum("amount"), 0, output_field=models.IntegerField()))['total_price']

#     @property
#     def total_payment_format_money(self):
#         return format_money(self.total_payment)



