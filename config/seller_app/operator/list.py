from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from order.models import Order
from user.models import User
from django.db.models import Q
from django.core.paginator import Paginator


@login_required(login_url='/login')
@permission_required('admin.seller_app_operator_list', login_url="/home")
def seller_app_operator_list(request):
    #    operator = User.objects.filter(type=3, is_active=True).order_by("is_active")
    operator = User.objects.filter(type=3, seller=request.user).order_by("-id")

    if request.GET.get("search", None):
        query = request.GET["search"]
        operator = operator.filter(
            Q(username__contains=query) | Q(first_name__contains=query) | Q(last_name__contains=query) | Q(
                operator_id__contains=query))

    if request.GET.get("operator", None):
        from django.utils import timezone
        from datetime import datetime, timedelta
        three_days_ago = timezone.now() - timezone.timedelta(days=4)
        grouped_operators = set(
            Order.objects.filter(created_at__gte=three_days_ago, operator__isnull=False).values_list('operator_id',
                                                                                                     flat=True))
        ten_days_ago = datetime.now() - timedelta(days=10)
        users = User.objects.filter(type=3, is_active=True, date_joined__lte=ten_days_ago).exclude(
            id__in=grouped_operators).update(is_active=False)
        messages.success(request, "Dostup olindi")
        return redirect('operator_management_list')

    paginator = Paginator(operator, 25)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/operator/list.html', {'page_obj': queryset, 'count': operator.count(),
                                                                      'active_count': operator.filter(
                                                                          is_active=True).count()})

