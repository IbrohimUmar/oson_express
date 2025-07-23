from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from config.export_excel import export_excel_from_driver_order_history
from order.models import Order
from user.models import User


@login_required(login_url='/login')
@permission_required('admin.driver_order_history', login_url="/home")
def driver_order_history(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    query = Order.objects.filter(driver=driver).order_by("-updated_at")
    status = request.GET.get("status", None)
    if status is not None and status != '0':

        if status == '55':
            query = query.filter(status='5', cancelled_status='1').order_by("-updated_at")
        elif status == '5555':
            query = query.filter(status='5', cancelled_status='2').order_by("-updated_at")
        elif status == '555':
            query = query.filter(status='5', cancelled_status='3').order_by("-updated_at")
        else:
            query = query.filter(status=status).order_by("-updated_at")

    if 'excel' in request.GET:
        params = request.GET.copy()
        if 'excel' in params:
            del params['excel']
        url = request.path + '?' + params.urlencode()
        messages.success(request, "Excelga import qilinmoqda...")
        # thread = threading.Thread(target=export_excel_from_driver_order_history,
        #                           args=(query,))
        # thread.start()
        export_excel_from_driver_order_history(query)
        return redirect(url)
    paginator = Paginator(query, 50)
    page_number = request.GET.get('page')
    order = paginator.get_page(page_number)
    return render(request, 'driver/order_history/history.html', {"d": driver, "order": order, 'page_obj': order})
