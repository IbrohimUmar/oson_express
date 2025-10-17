import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from config.postage.permission import logistic_branch_permission_required
from order.models import Order
from services.handle_exception import handle_exception
from services.seller.get_seller import get_seller
from user.models import User
from django.db.models import Q
from django.core.paginator import Paginator

from postage.models import Postage, PostageDetails, LogisticBranch


@login_required(login_url='/login')
@logistic_branch_permission_required('seller_details')
def postage_branch_seller_details(request, logistic_branch_id, postage_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    postage = get_object_or_404(Postage, Q(from_logistic_branch=logistic_branch) | Q(to_logistic_branch=logistic_branch), id=postage_id)
    details = PostageDetails.objects.filter(postage=postage)

    '''
    pocha haqida ma'lumotlar

    pasda belgilan pochtalar va kim tasdiqlab kim tasdiqlamagan ekanligi
    '''

    paginator = Paginator(details, 100)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'postage/branch/seller/details.html', {
        'postage': postage,
        'logistic_branch': logistic_branch,
        'queryset': queryset})

