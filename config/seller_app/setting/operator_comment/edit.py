from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from order.models import SellerOperatorStatusDesc
from services.seller.get_seller import get_seller


@permission_required('admin.seller_app_setting_operator_comment_edit', login_url="/home")
def seller_app_setting_operator_comment_edit(request, id):
    seller = get_seller(request.user)
    seller_operator_status_desc = get_object_or_404(SellerOperatorStatusDesc, id=id, seller=seller)
    if request.method == 'POST':
        seller_operator_status_desc.description=request.POST['desc']
        seller_operator_status_desc.status=request.POST['status']
        seller_operator_status_desc.save()
        messages.success(request, "Ma'lumotlar o'zgartirildi")
        return redirect('seller_app_setting_operator_comment_edit', id)
    return render(request, "seller_app/setting/operator_comment/edit.html", {'seller_operator_status_desc':seller_operator_status_desc})