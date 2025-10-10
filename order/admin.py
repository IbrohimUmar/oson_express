from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse

from .models import *


# Register your models here.


from django.contrib.admin.models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the resultes by users, content types and action flags
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message',
        'object_id'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
        'object_id',
        'change_message'
    ]



class OrderInline(admin.StackedInline):
    model = Order
    extra = 0

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    pass





@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_filter = ('codename', 'content_type')
    search_fields = ['codename']

# @admin.register(OrderSite)
# class OrderSiteAdmin(admin.ModelAdmin):
#     list_display = ['id', 'site','customer_name', 'customer_phone', 'region', 'district', 'street', 'order_date', 'delivered_date',
#                     'created_at', 'updated_at']
#     inlines = [OrderInline]
#     search_fields = ['id']


class OrderProductInline(admin.StackedInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ['created_at','updated_at']

    def has_change_permission(self, request, obj=None):
        return False

class OrderStatusHistoryInline(admin.StackedInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at', 'updated_at']

    def has_change_permission(self, request, obj=None):
        return False


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'site', 'site_order_id','status', 'driver', 'driver_fee','created_at', 'updated_at', 'delivered_date']
#     inlines = [OrderProductInline]
#     search_fields = ['id', 'customer_phone', 'site_order_id']

#     def has_delete_permission(self, request, obj=None):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_add_permission(self, request):
#         return False





from store.models import Product
class OrderProductFilter(admin.SimpleListFilter):
    title = 'Product'
    parameter_name = 'product'
    def lookups(self, request, model_admin):
        products = Product.objects.all()
        return [(product.id, product.name) for product in products]
    def queryset(self, request, queryset):
        if self.value():
            order_pro = set(OrderProduct.objects.filter(order__status=1, product_id=self.value()).values_list("order_id", flat=True))
            return Order.objects.filter(id__in=order_pro)
        else:
            return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def mahsulotlar(self):
        return list(self.order_products.values_list("product__name", flat=True))

    list_display = ['id', 'status', 'driver', mahsulotlar,'created_at', 'updated_at', 'delivered_date']
    inlines = [OrderProductInline, OrderStatusHistoryInline]
    search_fields = ['id', 'customer_phone']
    list_editable = ['status']
    list_filter = ["status", "created_at", OrderProductFilter]
    # readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        # readonly_fields.remove('status')
        # readonly_fields.remove('site_order_id')

        # for i in OrderProduct.objects.all():
        #     print(i.calculate_total_price())

        return readonly_fields

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


    def has_change_permission(self, request, obj=None):
        return False


#
# @admin.register(OrderProduct)
# class OrderProductAdmin(admin.ModelAdmin):
#     def holati(self):
#         if self.order:
#             return self.order.get_status_display()
#         return ""
#     def buyurtma_id(self):
#         if self.order:
#             return self.order.id
#         return ""
#
#     list_display = ['id', 'product', buyurtma_id,holati,'price','ordered_amount', 'created_at']
#     list_editable = ['ordered_amount', "price"]
#     list_filter = ['created_at']
#     ordering = ["created_at"]
#     search_fields = ['order__id']
#
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def has_add_permission(self, request):
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         # if request.user.is_superuser:
#         #     return True
#         return False


class MyAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        app_list += [
            {
                "name": "My Custom App",
                "app_label": "my_test_app",
                # "app_url": "/admin/test_view",
                "models": [
                    {
                        "name": "tcptraceroute",
                        "object_name": "tcptraceroute",
                        "admin_url": "/admin",
                        "view_only": True,
                    }
                ],
            }
        ]
        return app_list
