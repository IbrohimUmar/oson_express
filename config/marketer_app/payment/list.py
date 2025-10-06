from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render
from store.models import Product
from django.db.models import Q

from cash.models import UserBalanceManager

@login_required(login_url='/login')
@permission_required('admin.marketer_app_payment_list', login_url="/home")
def marketer_app_payment_list(request):
    payments = UserBalanceManager.objects.filter(type='1', user=request.user).order_by("-updated_at")
    status = request.GET.get("status", 'None')
    if status != 'None':
        payments = payments.filter(status=status)

    paginator = Paginator(payments, 50)
    payments_obj = paginator.get_page(int(request.GET.get("page", 1)))
    return render(request, 'marketer_app/payment/list.html', {'statuses':UserBalanceManager.status_choices,'page_obj': payments_obj, 'count': payments.count(),
                                                          })
