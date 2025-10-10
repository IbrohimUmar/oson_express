from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render
from order.models import SellerOperatorStatusDesc
from services.seller.get_seller import get_seller


@permission_required('admin.seller_app_setting_operator_comment_list', login_url="/home")
def seller_app_setting_operator_comment_list(request):
    seller = get_seller(request.user)
    comments = SellerOperatorStatusDesc.objects.filter(seller=seller)
    paginator = Paginator(comments, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, "seller_app/setting/operator_comment/list.html", {"page_obj": queryset, 'queryset_count':comments.count()})