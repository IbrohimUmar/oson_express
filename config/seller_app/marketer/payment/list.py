from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from cash.models import UserBalanceManager
from user.models import User



@login_required(login_url='/login')
@permission_required('admin.seller_app_marketer_payment_list', login_url="/home")
def seller_app_marketer_payment_list(request):
    # payments = UserBalanceManager.objects.filter(user__type='4')
    payments = UserBalanceManager.objects.all()
    if request.GET.get("search", None):
        query = request.GET["search"]
        print(query)
        # marketer = marketer.filter(
        #     Q(username__contains=query) | Q(first_name__contains=query) | Q(last_name__contains=query) | Q(
        #         operator_id__contains=query))

    user_id = request.GET.get("user_id", None)
    if user_id:
        print(user_id)
        user = None

    paginator = Paginator(payments, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/marketer/payment/list.html', {'page_obj': queryset, 'count':payments.count()})

