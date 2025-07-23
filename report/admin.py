from django.contrib import admin

# Register your models here.
from .models import DailyReport

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_main', 'date', 'created_at', 'main_balance']
    search_fields = ['id']
    list_filter = ['date']