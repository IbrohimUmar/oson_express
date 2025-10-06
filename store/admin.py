from django.contrib import admin
from .models import *
# Register your models here.
# admin.site.index_template = "home/index.html"

# admin.py faylingizga yozing
from django.contrib import admin
from .models import ProductApprovalNote

from django.forms import ModelForm
from django.forms.widgets import TextInput
from .models import Colors

class ColorsForm(ModelForm):
    class Meta:
        model = Colors
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }
        
        
        


@admin.register(ProductApprovalNote)
class ProductApprovalNoteAdmin(admin.ModelAdmin):
    list_display = ('product', 'user_display', 'note', 'created_at')
    list_filter = ('created_at', 'user', 'product')
    search_fields = ('note', 'product__name', 'user__username')

    def user_display(self, obj):
        return obj.user.username if obj.user else 'Anonim'
    user_display.short_description = 'Foydalanuvchi'



    
@admin.register(Colors)
class ColorsAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'color_box']
    list_display_links = ["id", "name"]
    form = ColorsForm
        




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ["id", "name"]



class MeasureItemInline(admin.StackedInline):
    model = MeasureItem
    extra = 0



@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'short_name', 'items_name']
    list_display_links = ["id", "name", "short_name"]
    search_fields = ['short_name', 'short_name']
    inlines = [MeasureItemInline]



    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False



        
class ProductDeliveryPriceInline(admin.StackedInline):
    model = ProductDeliveryPrice
    extra = 0

class ProductCollectionItemInline(admin.StackedInline):
    model = ProductCollectionItem
    extra = 0
    filter_horizontal = ['collection', ]


    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
# class InputProductInline(admin.StackedInline):
#     def kiritilgan_sana(self):
#         return self.created_at.strftime(("%Y-%m-%d"))
#     readonly_fields = [kiritilgan_sana, 'price']
#     exclude = ['input_product']

#     model = InputProductItems
#     extra = 0


#     def save_model(self, request, obj, form, change):
#         print(obj.amount)
#         super().save_model(request, obj, form, change)

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     def ombordagi_soni(self):
#         return self.amount
#     list_display = ['id', 'name', 'short', ombordagi_soni,'seller_fee', 'price']
#     search_fields = ['name', 'short']
#     #readonly_fields = [ombordagi_soni]
#     list_display_links = ["id", "name", 'short']
#     # list_editable = ['name', 'seller_fee']
#     inlines = [InputProductInline, ProductItemsInline, ProductDeliveryPriceInline]


#     def save_model(self, request, obj, form, change):

#         if change:
#             send_order_data_other_sites()
#         super().save_model(request, obj, form, change)

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'jami_kirim', 'jami_chiqim', 'jami_chiqim_yulda', 'jami_buyurtmalar_holati_buyicha']
#     search_fields = ['name', 'short']
#     inlines = [InputProductInline,ProductItemsInline, ProductDeliveryPriceInline]

#     def has_delete_permission(self, request, obj=None):
#         return False

#     def save_model(self, request, obj, form, change):
#         if change:
#             send_order_data_other_sites()
#         super().save_model(request, obj, form, change)








from order.models import Order, OrderProduct
from django.db.models import Q, ExpressionWrapper
# from warehouse.models import WarehouseOperationItemDetails, WareHouseStock


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def haydovchi_qulidagi_soni(self):
        driver_hand_product_price = \
            OrderProduct.objects.filter(status__in=[4, 6], product_id=self.id).exclude(
                order__status=4).aggregate(t=Coalesce(Sum('ordered_amount'), 0))['t']
        return driver_hand_product_price

    def jami_sotildi(self):
        driver_hand_product_price = \
            OrderProduct.objects.filter(status=4, order__status=4, product_id=self.id).aggregate(t=Coalesce(Sum('ordered_amount'), 0))['t']
        return driver_hand_product_price



    list_display = ['id', 'name']
    search_fields = ['name', 'short']
    inlines = [ProductCollectionItemInline]
    list_filter = ("is_active", "is_collection")
    # readonly_fields = ['id', 'name', 'short', 'seller_fee', 'measure','is_collection', 'price', 'bonus','bonus_type','bonus_amount', "is_active", "is_collection", 'colors', 'measure_item']
    list_per_page = 15

    def has_delete_permission(self, request, obj=None):
        return False


    # def has_change_permission(self, request, obj=None):
    #     return True



# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     def items_name(self):
#         return list(ProductItems.objects.filter(product_id=self.id).values_list('name', flat=True))

#     def total_order(self):
#         return OrderProduct.objects.filter(product_id=self.id).count()

#     def display_colors(self):
#         return [color.name for color in self.colors.all()]

#     def display_measure_item(self):
#         return [color.name for color in self.measure_item.all()]
#     list_display = ['id', 'name', 'short', 'seller_fee', 'measure', display_colors, display_measure_item,
#                     'is_collection', 'price', 'bonus', 'total_input', 'total_output', total_order,
#                     'defective_product_amount', 'return_product_amount', 'amount']
#     search_fields = ['name', 'short']
#     inlines = [ProductImageInline]
#     list_filter = ("is_active", "is_collection")
#     # readonly_fields = ['id', 'seller_fee', 'measure', 'price', 'bonus','bonus_type','bonus_amount', "is_active", 'colors', 'measure_item']

#     def has_delete_permission(self, request, obj=None):
#         return False


class ProductVariableInline(admin.StackedInline):
    model = ProductVariable
    extra = 0

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     def items_name(self):
#         return list(ProductItems.objects.filter(product_id=self.id).values_list('name', flat=True))

#     # def total_input(self):
#     #     return InputProductItems.objects.filter(product_id=self.id).count()
#     # def total_output(self):
#     #     return OutputProductItems.objects.filter(product_id=self.id).count()
#     def total_order(self):
#         return OrderProduct.objects.filter(product_id=self.id).count()
        

#     def display_colors(self):
#         return [color.name for color in self.colors.all()]

#     def display_measure_item(self):
#         return [color.name for color in self.measure_item.all()]
        
#     # def display_colors(self):
#     #     return ", ".join([color.name for color in self.colors.all()])

        
#     list_display = ['id', 'name', 'short', 'measure', 'is_collection','price', 'measure', display_colors, display_measure_item, 'is_active']
#     search_fields = ['id', 'name', 'short']
#     list_editable = ['is_collection',]
#     # inlines = [ProductSizeInline,ProductItemsInline, ProductDeliveryPriceInline, InputProductInline, ProductCollectionItemInline]
#     # inlines = [ProductSizeInline,ProductItemsInline, ProductDeliveryPriceInline]
#     list_filter = ("is_active", "is_collection")
#     inlines = [ProductDeliveryPriceInline, ProductItemsInline,ProductCollectionItemInline, ProductVariableInline]



#     def has_delete_permission(self, request, obj=None):
#         return False

#     def has_view_permission(self, request, obj=None):
#         if request.user.is_superuser:
#             return True
#         else:
#             return False
        
#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         send_order_data_other_sites()


from order.models import Order
class orderItemsInline(admin.StackedInline):
    model = Order
    extra = 0


#@admin.register(ProductItems)
class ProductItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'product','product_id','price', 'seller_fee', 'order_amount']
    search_fields = ['name', 'product__name']
#     list_editable = ['name', 'seller_fee', 'price']
    ordering = ['name']

