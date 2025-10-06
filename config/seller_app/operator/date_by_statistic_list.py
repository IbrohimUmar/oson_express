from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from user.models import User
from config.driver.daily_report import calculate_sales_percentage
from django.db.models import Count, Q, F
from django.utils import timezone


@login_required(login_url='/login')
@permission_required('admin.seller_app_operator_date_by_statistic', login_url="/home")
def seller_app_operator_date_by_statistic(request):
    now = timezone.now()
    # from_date = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    # to_date = request.GET.get("to_date", now.strftime("%Y-%m-%d"))
    from datetime import datetime, time, timedelta
    from_date_str = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    to_date_str = request.GET.get("to_date", now.strftime("%Y-%m-%d"))
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    from order.models import Order
    total_counts = Order.objects.filter(seller=request.user, updated_at__date__range=(from_date, to_date)).aggregate(
        accepted_count=Count('id', filter=Q(status=8)),
        being_archived_count=Count('id', filter=Q(status=7)),
        new_count=Count('id', filter=Q(status=1, operator__isnull=True)),
        new_count_received=Count('id', filter=Q(status=1, operator__isnull=False)),
        call_back_count=Count('id', filter=Q(status=6)),
        double=Count('id', filter=Q(status=9)),
        total_count=Count('id'),
        total_count_received=Count('id', filter=Q(operator__isnull=False)),
    )
    total_counts['sales_interest'] = calculate_sales_percentage(total_counts['accepted_count'], total_counts['total_count'])
    driver = User.objects.filter(type='3', seller=request.user, is_active=True).annotate(
        accepted_count=Count('operator', filter=Q(operator__status=8 ,operator__updated_at__date__range=(from_date, to_date))),
        being_archived_count=Count('operator', filter=Q(operator__status=7, operator__updated_at__date__range=(from_date, to_date))),
        new_count=Count('operator', filter=Q(operator__status=1, operator__updated_at__date__range=(from_date, to_date))),
        call_back_count=Count('operator', filter=Q(operator__status=6, operator__updated_at__date__range=(from_date, to_date))),
        total_count=Count('operator', filter=Q(operator__updated_at__date__range=(from_date, to_date))),
    ).order_by("-total_count").values('first_name', 'id',  'username', 'region__name' ,'last_name',
                                     'accepted_count', 'being_archived_count', 'new_count',
                                     'call_back_count', 'total_count')
    for d in driver:
        d['sales_interest'] = calculate_sales_percentage(d['accepted_count'], d['total_count'])
    # driver = sorted(driver, key=lambda d: float(d['sales_interest']), reverse=True)
    driver = sorted(driver, key=lambda d: float(d['total_count']), reverse=True)
    return render(request, 'seller_app/operator/date_by_statistic.html', {"driver" :driver, 'now' :now.strftime("%Y-%m-%d"), 'total_results' :total_counts})
