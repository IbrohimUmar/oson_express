from django.contrib import admin
from .models import *
# Register your models here.
from user.models import CashCategory, CashAllowedPaymentTypes
from django.db import transaction, IntegrityError
from config.cash.crud import cashier_balance_update
from django.shortcuts import redirect
from django.contrib import messages


class CashPersonalPayCardAdmin(admin.StackedInline):
    model = CashPersonalPaymentCard
    extra = 0


@admin.register(Cash)
class CashAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'from_user', 'to_user', "responsible", "category", "amount", "desc","created_at", 'updated_at']
    search_fields = ['id', "desc"]
    #inlines = [CashPersonalPayCardAdmin]
    list_filter = ["type", "category"]
    list_editable = ["category"]
    readonly_fields = ['responsible']


    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                cash = Cash.objects.get(id=obj.id)
                updated_cashier_balance = [cash.from_user.id,obj.from_user.id]
                if cash.to_user:
                    updated_cashier_balance.append(cash.to_user.id)
                if obj.to_user:
                    updated_cashier_balance.append(obj.to_user.id)
                obj.responsible =request.user
                super().save_model(request, obj, form, change)
                updated_cashier_balance = list(set(updated_cashier_balance))
                for u in set(updated_cashier_balance):
                    cashier_balance_update(u)
                messages.success(request,"O'zgartirildi")
        except IntegrityError as e:
            messages.error(request, f"Saqlashda xatolik {e}")
            return e
    def response_change(self, request, obj):
        return redirect(request.META.get('HTTP_REFERER', "cash"))

@admin.register(CashCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type']

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

@admin.register(UserBalanceManager)
class UserBalanceManagerAdmin(admin.ModelAdmin):
    pass

@admin.register(CashAllowedPaymentTypes)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False