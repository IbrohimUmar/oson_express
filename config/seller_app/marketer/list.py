from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from user.models import User



@login_required(login_url='/login')
@permission_required('admin.seller_app_marketer_list', login_url="/home")
def seller_app_marketer_list(request):
    seller = User.objects.filter(type=4, seller=request.user).order_by("-id")
    if request.GET.get("search", None):
        query = request.GET["search"]
        seller = seller.filter(
            Q(username__contains=query) | Q(first_name__contains=query) | Q(last_name__contains=query) | Q(
                operator_id__contains=query))

    paginator = Paginator(seller, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/marketer/list.html', {'page_obj': queryset,'count': seller.count(),
                                                                      'active_count': seller.filter(
                                                                          is_active=True).count()})

