from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render
from store.models import Product
from order.models import MarketerStream, Order, Status
from django.db.models import Q, Count


@login_required(login_url='/login')
@permission_required('admin.marketer_app_statistic_stream', login_url="/home")
def marketer_app_statistic_stream(request):
    streams = MarketerStream.objects.filter(marketer=request.user).order_by("-id")
    filter_query = request.GET.get("filter", None)
    if filter_query:
        streams = streams.filter(Q(name__contains=filter_query) | Q(product__name__contains=filter_query))

    paginator = Paginator(streams, 50)
    pagination_queryset = paginator.get_page(int(request.GET.get("page", 1)))

    page_streams = pagination_queryset.object_list.annotate(
        total_orders=Count('order'),
        status_1=Count('order', filter=Q(order__status='1')),  # Mahsulot kutilmoqda
        status_2=Count('order', filter=Q(order__status='2')),  # Mahsulot yuborildi
        status_3=Count('order', filter=Q(order__status='3')),  # Yetkazilmoqda
        status_4=Count('order', filter=Q(order__status='4')),  # Sotildi
        status_5=Count('order', filter=Q(order__status='5')),  # Bekor qilindi
        status_6=Count('order', filter=Q(order__status='6')),  # Qayta qo'ng'iroq
        status_7=Count('order', filter=Q(order__status='7')),  # Mahsulot belgilandi
        status_8=Count('order', filter=Q(order__status='8')),  # Qadoqlanmoqda
        status_9=Count('order', filter=Q(order__status='9')),  # Yangi
        status_10=Count('order', filter=Q(order__status='10')),  # Arxivlanmoqda
        status_11=Count('order', filter=Q(order__status='11')),  # Arxivlandi
        status_12=Count('order', filter=Q(order__status='12')),  # Double
    )
    return render(request, 'marketer_app/statistic/stream.html', {'quary': filter_query,'page_obj': pagination_queryset, 'page_streams':page_streams, 'count': streams.count(),
                                                          })
