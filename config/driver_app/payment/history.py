from asgiref.sync import async_to_sync, sync_to_async
from django.shortcuts import render

from cash.models import Cash
from user.models import TempPayment, User
from django.core.paginator import Paginator
from itertools import chain
from ..permission import is_driver


@is_driver
@async_to_sync
async def driver_app_payment_history(request):
    user = request.user

    type = request.GET.get("type", None)

    if type == '1':
        cash = list(Cash.objects.filter(from_user=user).order_by("-created_at"))
        combined_results = cash

    elif type == '2':
        combined_results = list(TempPayment.objects.filter(user=user).order_by("-created_at"))
    else:
        cash = list(Cash.objects.filter(from_user=user).order_by("-created_at"))
        old_payment = []
        temp_payment = list(TempPayment.objects.filter(user=user).order_by("-created_at"))
        combined_results = list(chain(temp_payment, cash, old_payment))

    paginator = Paginator(combined_results, 5)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    data = []
    for q in queryset:
        if q.__class__.__name__ == "Cash":
            if q.to_user:
                data.append({"id":q.id, 'amount':q.amount, 'desc':q.desc, 'created_at':q.created_at, 'model':q.__class__.__name__, 'to_user':f'{q.to_user.first_name} {q.to_user.last_name}'})
            else:
                data.append({"id":q.id, 'amount':q.amount, 'desc':q.desc, 'created_at':q.created_at, 'model':q.__class__.__name__, 'to_user':None, 'category':q.category.name})

        if q.__class__.__name__ == "DriverPayment":
            data.append({"id": q.id, 'amount': q.amount, 'desc': q.desc, 'created_at': q.created_at,
                         'model': q.__class__.__name__, 'to_user': None, 'category': None})

        if q.__class__.__name__ == "TempPayment":
            data.append({"id": q.id, 'amount': q.amount, 'desc': q.desc, 'created_at': q.created_at,
                         'model': q.__class__.__name__, 'to_user': q.cashier, 'category': q.category})

    return render(request, 'driver_app/payment/history.html',{'page_obj':queryset, 'count':len(combined_results), 'data':data})
