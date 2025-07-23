from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, redirect
import datetime
import calendar
from user.models import User
from order.models import Order

@login_required(login_url='/login')
@permission_required('admin.operator_app_monthly_report', login_url="/home")
def operator_app_monthly_report(request):
    def get_data_time_period(year, month):
        data = []
        last_day_month = list(calendar.monthrange(year, month))[1] + 1
        for i in range(1, last_day_month):
            data.append({
                'date': datetime.datetime(year, month, i), 'input_order': Order.objects.filter(
                    operator_id=request.user.id, created_at__year=year, created_at__month=month,
                    created_at__day=i).count(),
            })
        return data
    if request.method == 'POST':
        if request.POST.get("payment_card"):
            User.objects.filter(id=request.user.id).update(
                payment_card=request.POST["payment_card"]
            )
            messages.success(request, "Saqlandi")
            return redirect("operator_app_profile")


        year = int(request.POST['to'][:4])
        month = int(request.POST['to'][5:])
        data = get_data_time_period(year, month)
        total_order = sum([d['input_order'] for d in data])
        return render(request, 'operator_app/report/monthly.html',
                      {"o": request.user, 'data': data, 'dates': request.POST['to'], 'total_order':total_order, 'total_payment':0})
    today = datetime.date.today()
    data = get_data_time_period(today.year, today.month)
    total_order = sum([d['input_order'] for d in data])
    return render(request, 'operator_app/report/monthly.html', {"o": request.user, 'data': data, 'dates': today.strftime(("%Y-%m")), 'total_order':total_order})

