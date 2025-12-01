from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render

from services.seller.get_seller import get_seller
from user.models import User
from config.driver.daily_report import calculate_sales_percentage
from django.db.models import Count, Q, F
from django.utils import timezone


@login_required(login_url='/login')
@permission_required('admin.seller_app_operator_comment_date_by_statistic', login_url="/home")
def seller_app_operator_comment_date_by_statistic(request):
    now = timezone.now()
    seller = get_seller(request.user)
    # from_date = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    # to_date = request.GET.get("to_date", now.strftime("%Y-%m-%d"))
    from datetime import datetime, time, timedelta
    from_date_str = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    to_date_str = request.GET.get("to_date", now.strftime("%Y-%m-%d"))
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    from order.models import Order, SellerOperatorStatusDesc

    status_desc_all = SellerOperatorStatusDesc.objects.filter(seller=seller)

    orders = Order.objects.filter(seller=seller, operator_status_changed_at__date__range=(from_date, to_date))
    for i in status_desc_all:
        i.order_count = orders.filter(operator_comment=i).count()



    operators = User.objects.filter(type='3', seller=seller, is_active=True)

    paginator = Paginator(operators, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    page_operators = page_obj.object_list  # Sahifadagi operatorlar

    for operator in page_operators:
        stat = []
        for i in status_desc_all:
            stat.append(orders.filter(operator_comment=i).count())
        operator.stat = stat

    return render(request, 'seller_app/operator/comment_date_by_statistic.html', {
        'status_desc_all':status_desc_all,
        'operators': page_operators,
        'page_obj': page_obj,
        'now' :now.strftime("%Y-%m-%d")})
