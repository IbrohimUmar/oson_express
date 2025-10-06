# from django.contrib import admin
#
# # Register your models here.
# from .models import WareHouse, WareHouseStock, WareHouseStockHistory, WarehouseOperationItemDetails, WarehouseOperation, WarehouseOperationItem, WarehouseOperationAndOrderRelations
#
#
#
#
#
# @admin.register(WareHouse)
# class WareHouseAdmin(admin.ModelAdmin):
#     list_display = ['id', 'type', 'name', 'responsible']
#
#
#
# class WareHouseStockHistoryInline(admin.StackedInline):
#     model = WareHouseStockHistory
#     extra = 0
#
#
#     def has_change_permission(self, request, obj=None):
#         return False
#
# @admin.register(WareHouseStock)
# class WareHouseStockAdmin(admin.ModelAdmin):
#     list_display = ['id', 'warehouse', 'user', 'product', 'product_variable',
#                     'input_price', 'selling_price', 'amount']
#     list_filter = ['warehouse']
#     search_fields = ['product__name']
#     readonly_fields = ['user', 'warehouse', 'product', 'product_variable']
#     inlines = [WareHouseStockHistoryInline]
#
#
#     def has_change_permission(self, request, obj=None):
#         return False
#
#
#
#
# @admin.register(WareHouseStockHistory)
# class WareHouseStockHistoryAdmin(admin.ModelAdmin):
#     list_display = ['id', 'model_name', 'warehouse_stock_id', 'amount', 'obj_id',
#                     'expired_date', 'created_at']
#     search_fields = ['warehouse_stock__id']
#
#
#     def has_change_permission(self, request, obj=None):
#         return False
#
#
#
# class WarehouseOperationItemInline(admin.StackedInline):
#     model = WarehouseOperationItem
#     extra = 0
#
#
# @admin.register(WarehouseOperation)
# class WarehouseOperationAdmin(admin.ModelAdmin):
#     list_display = ['id', 'action', 'from_warehouse', 'from_warehouse_status', 'to_warehouse', 'to_warehouse_status','responsible', 'created_at']
#     list_filter = ['action', 'from_warehouse_status', 'to_warehouse_status']
#     # inlines = [WarehouseOperationItemInline,]
#
#
#
#
#
# @admin.register(WarehouseOperationItem)
# class WarehouseOperationItemAdmin(admin.ModelAdmin):
#     list_display = ['id', 'warehouse_operation', 'product', 'product_variable', 'warehouse_stock',
#                     'input_price', 'selling_price', 'amount', 'updated_at']
#     search_fields = ['warehouse_operation__id']
#
#
#
# @admin.register(WarehouseOperationItemDetails)
# class WarehouseOperationItemDetailsAdmin(admin.ModelAdmin):
#     list_display = ['id', 'from_warehouse_operation', 'from_warehouse_operation_item', 'from_warehouse_stock',
#                     'warehouse_operation',
#                     'warehouse_operation_item', 'warehouse_stock', 'product', 'leave_amount', 'input_price','updated_at']
#     search_fields = ['id']
#
#
#
#
# @admin.register(WarehouseOperationAndOrderRelations)
# class WarehouseOperationAndOrderRelationsAdmin(admin.ModelAdmin):
#     list_display = ['id', 'action', 'warehouse_operation',
#                     'order', 'created_at']
#     search_fields = ['order__id', 'warehouse_operation__id']
#
#
# # @admin.register(WarehouseOperationItemTransfer)
# # class WarehouseOperationItemTransferAdmin(admin.ModelAdmin):
# #     list_display = ['id', 'from_warehouse_operation_item', 'to_warehouse_operation_item',
# #                     'to_order_product', 'amount', 'created_at', 'updated_at']


from django.contrib import admin
from .models import (
    WareHouse, WarehousePermission, WarehouseOperation,
    WareHouseStock, WarehouseOperationAndOrderRelations, WarehouseStockAttachmentOrder, OrderWarehouseAction
)


@admin.register(WareHouse)
class WareHouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'responsible', 'created_at')
    list_filter = ('type',)
    search_fields = ('responsible__username',)
    autocomplete_fields = ['responsible']
    ordering = ['-created_at']


@admin.register(WarehousePermission)
class WarehousePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'warehouse', 'input_product', 'transit_product', 'residue')
    list_filter = ('warehouse', 'user')
    search_fields = ('user__username',)
    autocomplete_fields = ['user', 'warehouse']


@admin.register(WarehouseOperation)
class WarehouseOperationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'action', 'status', 'seller', 'supplier', 'from_warehouse', 'to_warehouse',
        'created_at', 'status_changed_user'
    )
    list_filter = ('action', 'status')
    search_fields = ('seller__username', 'supplier__username')
    autocomplete_fields = ['seller', 'supplier', 'from_warehouse', 'to_warehouse', 'status_changed_user']


@admin.register(WareHouseStock)
class WareHouseStockAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'warehouse', 'product', 'product_variable', 'quantity', 'input_price',
        'status', 'lot_number', 'created_at'
    )
    list_filter = ('warehouse', 'status')
    # search_fields = ('product__name')


@admin.register(WarehouseOperationAndOrderRelations)
class WarehouseOperationAndOrderRelationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse_operation', 'order', 'created_at')
    list_filter = ('warehouse_operation',)
    search_fields = ('order__id',)
    autocomplete_fields = ['warehouse_operation', 'order']



@admin.register(WarehouseStockAttachmentOrder)
class WarehouseStockAttachmentOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse', 'product', 'warehouse_quantity', 'attachment_amount')
    search_fields = ('id',)


@admin.register(OrderWarehouseAction)
class OrderWarehouseActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse', 'type', 'order', 'responsible')
    list_filter = ['type']
