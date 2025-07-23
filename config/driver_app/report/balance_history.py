from asgiref.sync import async_to_sync
from django.shortcuts import render
from config.driver_app.permission import is_driver
from report.models import DriverReport
import datetime


@is_driver
@async_to_sync
async def driver_app_report_balance_history(request):
    date_input = request.GET.get('date', None)
    if date_input:
        try:
            date = datetime.datetime.strptime(date_input, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.datetime.now().date()
    else:
        date = datetime.datetime.now().date()
    reports = DriverReport.objects.filter(driver=request.user, created_at__date=date).order_by("-created_at")
    return render(request, 'driver_app/report/balance_history.html', {"reports": reports, 'date':date})
