from asgiref.sync import async_to_sync
from django.shortcuts import render
from config.driver_app.permission import is_driver

@is_driver
@async_to_sync
async def driver_app_report_main(request):
    report = request.user.driver_data
    return render(request, 'driver_app/report/main.html',{"balance":report.balance_uzs, 'report':report, 'order_status_by':report.order_status_by, "order_product_by_uzs":report.order_product_by_uzs})
