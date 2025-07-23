from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404

from user.models import User


@login_required(login_url='/login')
@permission_required('admin.driver_main_report', login_url="/home")
def driver_main_report(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    report = driver.driver_data
    return render(request, 'driver/report/main_report.html', {"d":driver,
                                                              "balance": report.balance_uzs, 'report': report,
                                                               'order_status_by': report.order_status_by,
                                                               "order_product_by_uzs": report.order_product_by_uzs
                                                              })

