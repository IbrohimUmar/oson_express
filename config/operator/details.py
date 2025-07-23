from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from order.models import Order
from user.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
import datetime
import calendar


@login_required(login_url='/login')
@permission_required('admin.operator_details', login_url="/home")
def operator_details(request, id):
    operator = get_object_or_404(User, id=id, type=3)
    if request.method == 'POST':
        year = int(request.POST['to'][:4])
        month = int(request.POST['to'][5:])
        data = []
        last_day_month = list(calendar.monthrange(year, month))[1] + 1
        for i in range(1, last_day_month):
            data.append({
                'date': datetime.datetime(year, month, i), 'input_order': Order.objects.filter(
                    operator_id=id, created_at__year=year, created_at__month=month, created_at__day=i).count(),
                'payment': 0
            })
        total_order = sum([d['input_order'] for d in data])
        total_payment = sum([d['payment'] for d in data])
        return render(request, 'operator/details.html',
                      {"o": operator, 'data': data, 'dates': request.POST['to'], 'total_order': total_order,
                       'total_payment': total_payment})

    today = datetime.date.today()
    last_day_month = list(calendar.monthrange(2023, today.month))[1] + 1
    data = []
    for i in range(1, last_day_month):
        data.append({
            'date': datetime.datetime(today.year, today.month, i), 'input_order': Order.objects.filter(
                operator_id=id, created_at__year=today.year, created_at__month=today.month, created_at__day=i).count(),
            'payment': 0
        })
    total_order = sum([d['input_order'] for d in data])
    total_payment = sum([d['payment'] for d in data])
    return render(request, 'operator/details.html',
                  {"o": operator, 'data': data, 'dates': today.strftime(("%Y-%m")), 'total_order': total_order,
                   'total_payment': total_payment})



@login_required(login_url='/login')
@permission_required('admin.operator_details', login_url="/home")
def operator_details_order(request, id, year, month, day):
    operator = get_object_or_404(User, id=id, type=3)
    order = Order.objects.filter(operator_id=id, created_at__year=year, created_at__month=month, created_at__day=day)
    return render(request, 'operator/details_orders.html',
                  {"o": operator, 'order': order, 'date': datetime.datetime(year, month, day)})
