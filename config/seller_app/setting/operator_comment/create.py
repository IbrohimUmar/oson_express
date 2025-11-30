from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from order.models import SellerOperatorStatusDesc
from services.seller.get_seller import get_seller


@permission_required('admin.seller_app_setting_operator_comment_create', login_url="/home")
def seller_app_setting_operator_comment_create(request):
    seller = get_seller(request.user)
    if request.method == 'POST':
        SellerOperatorStatusDesc.objects.create(
            seller=seller,
            description=request.POST['desc'],
            status=request.POST['status'],
            is_desc_required={'0':False, '1':True}.get(request.POST['is_desc_required'], '0'),
        )
        messages.success(request, "Ma'lumotlar saqlandi")
        return redirect('seller_app_setting_operator_comment_list')

    return render(request, "seller_app/setting/operator_comment/create.html", {})