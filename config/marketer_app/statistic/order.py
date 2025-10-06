from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render
from store.models import Product
from order.models import Order, Status
from django.db.models import Q

@login_required(login_url='/login')
@permission_required('admin.marketer_app_statistic_order', login_url="/home")
def marketer_app_statistic_order(request):
    orders = Order.objects.filter(marketer=request.user).order_by("-updated_at")
    status = request.GET.get("status", 'None')
    if status != 'None':
        orders = orders.filter(status=status)
    filter_query = request.GET.get("filter", None)
    if filter_query:
        orders = orders.filter(Q(id__contains=filter_query) | Q(customer_phone__contains=filter_query) | Q(site_order_id__contains=filter_query))

    paginator = Paginator(orders, 50)
    order = paginator.get_page(int(request.GET.get("page", 1)))
    return render(request, 'marketer_app/statistic/order.html', {'statuses':Status, 'quary': filter_query,'page_obj': order, "order": order, 'count': orders.count(),
                                                          })
