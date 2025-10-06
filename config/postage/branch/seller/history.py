import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from order.models import Order
from user.models import User
from warehouse.models import WarehouseOperation, WareHouse, WarehousePermission
from postage.models import Postage, LogisticBranch, LogisticBranchPermission, PostageDetails
from config.postage.permission import logistic_branch_permission_required


@login_required(login_url='/login')
# @logistic_branch_permission_required('seller_return')
def postage_branch_seller_history(request, logistic_branch_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    logistic_branch.perms = logistic_branch.get_user_permission(request.user)
    postage_qs = Postage.objects.filter(Q(from_logistic_branch=logistic_branch)|Q(to_logistic_branch=logistic_branch), action__in=['1','2'])
    sellers = User.objects.filter(type='6', is_active=True)
    '''
    buyerdan fileal tasdiqlariham bo'lishi kerak pochta qabul qilish ni tasdiqlash
    yoki pochta yuborishni tasdiqlash
    
    
    1. agar seller pochta topshirishni boshlagan bo'lsa 
    amaliyotni seller boshlaydi
    ichida harbir pochtani skannerlab olish imkoniyati bo'lishi kerak
    va hammasi tasdiqlanganidan keyin tasdiqlash knopkasi ko'rinishi kerak

    '''

    action = request.GET.get("action", '0')
    if action != '0':
        postage_qs = postage_qs.filter(action=action)

    from_user_status = request.GET.get("from_user_status", '0')
    if from_user_status != '0':
        postage_qs = postage_qs.filter(from_user_status=from_user_status)

    to_user_status = request.GET.get("to_user_status", '0')
    if to_user_status != '0':
        postage_qs = postage_qs.filter(to_user_status=to_user_status)


    if request.method == 'POST':
        print(request.POST)
        action = request.POST['action']

        postage = Postage.objects.filter(Q(from_logistic_branch=logistic_branch)|Q(to_logistic_branch=logistic_branch), id=request.POST['postage_id']).first()

        if not postage:
            messages.error(request, "Bunday pochta mavjud emas")
            return redirect('postage_branch_seller_history', logistic_branch_id)

        if postage.action == '2' and action == 'cancel' and postage.from_user_status == '2' and postage.to_user_status == '3':  # seller pochta topshirish bekor qilinsa
            postage.from_user_status = '3'
            postage.from_user_status_changed_at = datetime.datetime.now()
            postage.save()
            postage_orders_id = list(PostageDetails.objects.filter(postage=postage).values_list("order_id", flat=True))
            Order.objects.filter(id__in=postage_orders_id).update(transaction_lock=False)

            messages.success(request, "Bekor qilindi")
            return redirect('postage_branch_seller_history', logistic_branch_id)



    paginator = Paginator(postage_qs, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'postage/branch/seller/history.html', {"logistic_branch": logistic_branch,
                                                 'page_obj': queryset,
                                                 'sellers': sellers,
                                                 'count': postage_qs.count(),
                                                 })