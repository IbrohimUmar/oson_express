from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from user.models import User

@permission_required('admin.seller_statistic_list', login_url="/")
def seller_statistic_list(request):
    sellers = User.objects.filter(type=6).order_by("-id")

    if request.GET.get("search", None):
        query = request.GET["search"]
        supplier = sellers.filter(
            Q(username__contains=query) | Q(first_name__contains=query) | Q(last_name__contains=query))

    paginator = Paginator(sellers, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller/statistic_list.html', {'page_obj': queryset, 'count': sellers.count()})
