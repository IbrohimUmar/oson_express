from django.contrib import admin
from .models import LogisticBranch, LogisticBranchPermission, Postage, PostageDetails


@admin.register(LogisticBranch)
class LogisticBranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "region", "district", "created_at")
    list_filter = ("type", "region", "district")
    search_fields = ("name", "address")


@admin.register(LogisticBranchPermission)
class LogisticBranchPermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "logistic_branch", "user", "has_view", "seller_input", "seller_return", "driver_out", "driver_return", "transfer", "history", "residue")
    list_filter = ("logistic_branch", "user", "has_view", "seller_input", "driver_out")
    search_fields = ("user__username", "logistic_branch__name")


@admin.register(Postage)
class PostageAdmin(admin.ModelAdmin):
    list_display = (
        "id", "action", "from_logistic_branch", "from_user", "from_user_status",
        "to_logistic_branch", "to_user", "to_user_status", "created_at"
    )
    list_filter = ("action", "from_user_status", "to_user_status")
    search_fields = (
        "from_logistic_branch__name", "from_user__username",
        "to_logistic_branch__name", "to_user__username"
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(PostageDetails)
class PostageDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "postage", "order", "scan_from_user", "scan_to_user", "created_at")
    list_filter = ("scan_from_user", "scan_to_user")
    search_fields = ("order__id", "postage__id")
