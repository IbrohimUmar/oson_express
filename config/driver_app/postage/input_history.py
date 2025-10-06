from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from config.driver_app.permission import is_driver
from warehouse.models import WarehouseOperation
from postage.models import Postage, PostageDetails
from django.db.models import Q


@is_driver
def driver_app_postage_input_history(request):
    driver = request.user
    postage_qs = Postage.objects.filter(Q(from_user=driver)|Q(to_user=driver))
    paginator = Paginator(postage_qs, 10)
    page_number = request.GET.get('page', 1)
    queryset = paginator.get_page(page_number)
    return render(request, 'driver_app/postage/input_history.html',{'page_obj':queryset, 'count':postage_qs.count()})