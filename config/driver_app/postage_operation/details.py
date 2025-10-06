from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from config.driver_app.permission import is_driver
from warehouse.models import WarehouseOperation
from postage.models import Postage, PostageDetails
from django.db.models import Q


@is_driver
def driver_app_postage_operation_details(request, postage_id):
    driver = request.user
    postage = get_object_or_404(Postage, Q(from_user=driver) | Q(to_user=driver), id=postage_id)
    details = PostageDetails.objects.filter(postage=postage)

    paginator = Paginator(details, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'driver_app/postage_operation/details.html', {'postage': postage, 'queryset': queryset})