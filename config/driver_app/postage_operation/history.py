from asgiref.sync import async_to_sync
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from config.driver_app.permission import is_driver
from order.models import Order
from services.handle_exception import handle_exception
from warehouse.models import WarehouseOperation
from postage.models import Postage, PostageDetails
from django.db.models import Q
import datetime
from django.db import transaction


@is_driver
def driver_app_postage_operation_history(request):
    driver = request.user
    postage_qs = Postage.objects.filter(Q(from_user=driver)|Q(to_user=driver)).order_by('-id')
    paginator = Paginator(postage_qs, 10)

    if request.method == 'POST':
        print(request.POST)
        action = request.POST['action_type']
        postage_id = request.POST['postage']
        try:
            with transaction.atomic():

                if action == 'cancel':
                    postage = Postage.objects.filter(id=postage_id, action='4', from_user_status='2', to_user_status='3').first()
                    if not postage:
                        messages.error(request, "Pochta topilmadi")
                        return redirect("driver_app_postage_operation_history")

                    postage.from_user_status = '3'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    postage_details = PostageDetails.objects.filter(postage=postage)

                    Order.objects.filter(
                                id__in=list(postage_details.values_list('order_id', flat=True))
                            ).update(transaction_lock=False)

                    messages.success(request, "O'zgartirildi")
                    return redirect("driver_app_postage_operation_history")

                messages.error(request, "Iltimos qayta urinib ko'ring")
                return redirect("driver_app_postage_operation_history")
        except Exception as e:
            handle_exception(e)
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('driver_app_postage_operation_history')

    page_number = request.GET.get('page', 1)
    queryset = paginator.get_page(page_number)
    return render(request, 'driver_app/postage_operation/history.html', {'page_obj':queryset, 'count':postage_qs.count()})