from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from services.seller.get_seller import get_seller
from user.models import User
from config.driver.daily_report import calculate_sales_percentage
from django.db.models import Count, Q, F
from django.utils import timezone


@login_required(login_url='/login')
@permission_required('admin.seller_app_operator_date_by_statistic', login_url="/home")
def seller_app_operator_date_by_statistic(request):
    now = timezone.now()
    seller = get_seller(request.user)
    # from_date = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    # to_date = request.GET.get("to_date", now.strftime("%Y-%m-%d"))
    from datetime import datetime, time, timedelta
    from_date_str = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    to_date_str = request.GET.get("to_date", now.strftime("%Y-%m-%d"))
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    from order.models import Order
    total_counts = Order.objects.filter(seller=seller, created_at__date__range=(from_date, to_date)).aggregate(
        accepted_count=Count('id', filter=Q(status__in=[1, 7, 8, 2, 13, 3, 4, 5, 13, 15])),
        being_archived_count=Count('id', filter=Q(status=10)),
        new_count=Count('id', filter=Q(status=9, operator__isnull=True)),
        new_count_received=Count('id', filter=Q(status=9, operator__isnull=False)),
        call_back_count=Count('id', filter=Q(status=6)),
        double=Count('id', filter=Q(status=12)),
        total_count=Count('id'),
        total_count_received=Count('id', filter=Q(operator__isnull=False)),
    )
    total_counts['sales_interest'] = calculate_sales_percentage(total_counts['accepted_count'], total_counts['total_count'])
    driver = User.objects.filter(type='3', seller=seller, is_active=True).annotate(
        accepted_count=Count('operator', filter=Q(operator__status__in=[1, 7, 8, 2, 13, 3, 4, 5, 13, 15], operator__created_at__date__range=(from_date, to_date))),
        being_archived_count=Count('operator', filter=Q(operator__status=10, operator__created_at__date__range=(from_date, to_date))),
        new_count=Count('operator', filter=Q(operator__status=9, operator__created_at__date__range=(from_date, to_date))),
        call_back_count=Count('operator', filter=Q(operator__status=6, operator__created_at__date__range=(from_date, to_date))),
        total_count=Count('operator', filter=Q(operator__created_at__date__range=(from_date, to_date))),
    ).order_by("-total_count").values('first_name', 'id',  'username', 'region__name' ,'last_name',
                                     'accepted_count', 'being_archived_count', 'new_count',
                                     'call_back_count', 'total_count')
    for d in driver:
        d['sales_interest'] = calculate_sales_percentage(d['accepted_count'], d['total_count'])
    # driver = sorted(driver, key=lambda d: float(d['sales_interest']), reverse=True)
    driver = sorted(driver, key=lambda d: float(d['total_count']), reverse=True)
    return render(request, 'seller_app/operator/date_by_statistic.html', {"driver" :driver, 'now' :now.strftime("%Y-%m-%d"), 'total_results' :total_counts})
