from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render
from warehouse.models import WarehouseOperation, WareHouse, WarehousePermission
from postage.models import Postage, LogisticBranch, LogisticBranchPermission


@login_required(login_url='/login')
@permission_required('admin.postage_main', login_url="/home")
def postage_main(request):
    '''
    seller bo'lsa
    yoki dostup berilgan bo'lsa
    '''

    logistic_branch_permission = LogisticBranchPermission.objects.filter(user=request.user)
    logistic_branch_id = list(logistic_branch_permission.filter(has_view=True).values_list('logistic_branch_id', flat=True))
    logistic_branches = LogisticBranch.objects.filter(id__in=logistic_branch_id)
    for branch in logistic_branches:
        branch.perms = branch.get_user_permission(request.user)
    return render(request, 'postage/main.html', {"logistic_branches": logistic_branches})