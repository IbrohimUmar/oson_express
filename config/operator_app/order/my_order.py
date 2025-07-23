from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from django.db import models, IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect


from config.operator_app.permission import check_work_hours
from order.models import Order, CustomStatusDesc
from services.order.history import save_order_status_history


@login_required(login_url='/login')
@permission_required('admin.operator_app_my_order', login_url="/home")
@check_work_hours
def operator_app_my_order(request):
    order = Order.objects.filter(status__in=[9, 6], operator=request.user).order_by('-updated_at')
    statistic = Order.objects.filter(status__in=[9, 6], operator=request.user).aggregate(
        taked_new_order=models.Count("id", filter=models.Q(status=9)),
        call_back=models.Count("id", filter=models.Q(status=6)),
        total_order=models.Count("id"),
    )
    if request.GET.get("status", None):
        order = order.filter(status=int(request.GET["status"]))
    if request.method == "POST":
        try:
            with transaction.atomic():
                r = request.POST
                order = Order.objects.filter(id=r['id'], status__in=[9, 6], operator=request.user).first()
                if order:
                    status_and_desc = get_object_or_404(CustomStatusDesc, id=r['status_description'])
                    order.status = status_and_desc.status
                    order.note = status_and_desc.description
                    order.save()
                    save_order_status_history(order, order.status, "Operator buyurtmani izohini o'zgartirdi", request.user,
                                              'config.operator_app.order.my_order')
                    messages.success(request, "Saqlandi")
                    return redirect('operator_app_my_order')
                messages.error(request, "Buyurtmani o'zgartirishga kech qoldingiz")
                return redirect('operator_app_my_order')
        except IntegrityError as e:
            messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
            return redirect('operator_app_my_order')

    descriptions = CustomStatusDesc.objects.filter(Q(user=request.user) | Q(user=None))
    order_object = Paginator(order, 25)
    page_number = request.GET.get('page')
    order = order_object.get_page(page_number)

    return render(request, 'operator_app/order/my_order.html',
                  {"order": order, "statistic": statistic, "o": request.user, "descriptions": descriptions})
