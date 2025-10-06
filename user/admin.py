from django.contrib import admin, messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils.safestring import mark_safe

from .models import *
# Register your models here.


@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    list_display = ['id','name']


@admin.register(ExportedFile)
class ExportedFileAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'is_view_user']


@admin.register(Districts)
class DistrictsAdmin(admin.ModelAdmin):
    list_display = ['id','region', 'name', 'driver_fee', 'is_active', 'driver_is_bonus', 'driver_one_day_bonus', 'driver_two_day_bonus']
    list_editable = ['is_active','driver_fee', 'driver_is_bonus', 'driver_one_day_bonus', 'driver_two_day_bonus']
    search_fields = ['name']
    list_filter = ['region']
    exclude = ['distance']

    def has_delete_permission(self, request, obj=None):
        return False


class CashUserInline(admin.TabularInline):
    model = CashierUser
    extra = 0
    readonly_fields = ['balance']
    # def has_delete_permission(self, request, obj=None):
    #     return False    
    
    
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def ism_familiyasi(self):
        return self.first_name +" "+self.last_name

    list_display = ['username', ism_familiyasi, 'operator_id', 'region', 'district', 'is_active', 'type', 'fee_is_special','special_fee_amount']
    list_display_links = [ 'username', ism_familiyasi]
    search_fields = ['username', 'first_name', 'last_name']
    list_filter = ['region', 'is_active', 'cashier']
    # readonly_fields = [Sotildi,'last_login', 'date_joined', "user_permissions", 'groups', 'email', 'birthday', 'my_unique_code', 'tg_user_id', Daromadi, Qarzi]
    # fields = ['username']
    fields = ['username', 'password', 'password_text','first_name', 'last_name', 'type', 'cashier','is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions', 'fee_is_special','special_fee_amount']
    # list_editable = ['type', 'operator_id']
    filter_horizontal = ("groups", "user_permissions")  
    inlines = [CashUserInline]
    
    def has_delete_permission(self, request, obj=None):
        return False

    # def save_model(self, request, obj, form, change):
    #
    #     print(request.POST)
    #     password = make_password(request.POST['password'])
    #     # print(password)
    #     # form.data['password']=password
    #     # request.POST['password']=password
    #     if form.is_valid():
    #         # form.cleaned_data['password']='salom'
    #         # request.POST['password']='salom'
    #         # print(form.cleaned_data['password'])
    #         form.save()

    def save_model(self, request, obj, form, change):
        try:
            user_database = User.objects.get(pk=obj.pk)
        except Exception:
            user_database = None
        if user_database is None \
                or not (check_password(form.data['password'], user_database.password)
                        or user_database.password == form.data['password']):
            obj.password = make_password(obj.password)
        else:
            obj.password = user_database.password
        
        # send_order_data_other_sites()
        super().save_model(request, obj, form, change)

@admin.register(MarkedDeliveryPrice)
class MarkedDeliveryPrice(admin.ModelAdmin):
    list_display = ['amount', 'updated_at']
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


#@admin.register(OperatorFeeAmount)
class OperatorFeeAmount(admin.ModelAdmin):
    list_display = ['amount', 'updated_at']
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Concourse)
class ConcourseAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'start_data', 'finish_data', 'is_active']
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    def has_add_permission(self, request):
        if Concourse.objects.filter(type='1').exists() and Concourse.objects.filter(type='2').exists():
            return False
        return True


    def save_model(self, request, obj, form, change):
        if Concourse.objects.filter(type=obj.type).exclude(id=obj.id).exists():
            messages.error(request, "Haydovchi va operatorlar uchun 1 tadan konkurs qo'shishingiz mumkin")
            return False
        super().save_model(request, obj, form, change)
