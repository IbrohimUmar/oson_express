from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from order.models import Order
from postage.models import LogisticBranch
from user.models import User
from django.db.models import Q
from config.postage.permission import logistic_branch_permission_required

@login_required(login_url='/login')
@logistic_branch_permission_required('residue')
def postage_branch_residue(request, logistic_branch_id):

    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    orders = Order.objects.filter(logistic_branch_id=logistic_branch_id, status__in=['13', '14'])
    seller = User.objects.filter(type='6')

    if request.GET.get("search", None):
        query = request.GET["search"]
        orders = orders.filter(Q(id__icontains=query)|Q(barcode__icontains=query))

    if request.GET.get("status", '0') != '0':
        print('status bor')
        orders = orders.filter(status=request.GET['status'])

    if request.GET.get("seller", '0') != '0':
        print('seller bor')
        orders = orders.filter(seller_id=request.GET['seller'])

    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'postage/branch/residue.html', {
                                                            "logistic_branch": logistic_branch,
                                                            "seller": seller,
                                                           'page_obj': queryset, 'queryset_count':orders.count()})
