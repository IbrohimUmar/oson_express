from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render

from config.settings.base import TOLL_AMOUNT
from store.models import Product
from order.models import MarketerStream
from django.db.models import Q
@login_required(login_url='/login')
@permission_required('admin.marketer_app_stream_list', login_url="/home")
def marketer_app_stream_list(request):
    steams = MarketerStream.objects.filter(is_delete=False, marketer=request.user).order_by("-id")
    if request.GET.get("search", None):
        query = request.GET["search"]
        steams = steams.filter(Q(name__icontains=query)|Q(product__name__icontains=query))
    paginator = Paginator(steams, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    url = f"{request.scheme}://{request.META['HTTP_HOST']}/stream/"
    return render(request, 'marketer_app/stream/list.html', {'queryset': queryset, 'order': queryset, 'url': url, "TOLL_AMOUNT": TOLL_AMOUNT})
