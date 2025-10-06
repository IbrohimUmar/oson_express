import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from order.models import Order
from services.handle_exception import handle_exception
from services.seller.get_seller import get_seller
from user.models import User
from django.db.models import Q
from django.core.paginator import Paginator

from postage.models import Postage, PostageDetails


@login_required(login_url='/login')
@permission_required('admin.seller_app_postage_history', login_url="/home")
def seller_app_postage_history(request):
    seller = get_seller(request.user)
    postage_qs = Postage.objects.filter(Q(from_user=seller, action='1') | Q(to_user=seller, action='2'))

    if request.method == 'POST':

        try:
            with transaction.atomic():
                '''
                sellerdan pochta chiqim qilishda tasdiqlash bosilsa 
                postani tasdiqlandiga o'zgartirish
                '''
                action = request.POST['action']
                postage = Postage.objects.filter(Q(from_user=seller)|Q(to_user=seller), id=request.POST.get('postage_id', 0)).first()
                if not postage:
                    messages.error(request, "Bunday pochta mavjud emas")

                if postage.from_user_status != '1':
                    messages.error(request, "Pochtani holatini o'zgartirish mumkun emas")

                if postage.action == '1' and action == 'confirm': #seller pochta topshirish tasdiqlandi
                    '''
                    pochta holatini o'zgartirilsa bo'ldi
                    '''
                    postage.from_user_status='2'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    messages.success(request, "Tasdiqlandi")

                if postage.action == '1' and action == 'cancel': #seller pochta topshirish bekor qilinsa

                    postage.from_user_status='3'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    postage_orders_id = list(PostageDetails.objects.filter(postage=postage).values_list("order_id", flat=True))
                    Order.objects.filter(id__in=postage_orders_id, status='2', seller=seller).update(transaction_lock=False)
                    messages.success(request, "Bekor qilindi")

                if postage.action == '1' and action == 'cancel_because_to_user_cancel': #qabul qiluvchi fileal bekor qildi
                    postage.from_user_status='3'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()
                    postage_orders_id = list(PostageDetails.objects.filter(postage=postage).values_list("order_id", flat=True))
                    Order.objects.filter(id__in=postage_orders_id, status='2', seller=seller).update(transaction_lock=False)
                    messages.success(request, "Bekor qilindi")

                return redirect('seller_app_postage_history')

        except Exception as e:
            handle_exception(e)
            return JsonResponse({
                'status': 404,
                'message': f"{e}",
            })


    action = request.GET.get("action", '0')
    if action != '0':
        postage_qs = postage_qs.filter(action=action)

    from_user_status = request.GET.get("from_user_status", '0')
    if from_user_status != '0':
        postage_qs = postage_qs.filter(from_user_status=from_user_status)

    to_user_status = request.GET.get("to_user_status", '0')
    if to_user_status != '0':
        postage_qs = postage_qs.filter(to_user_status=to_user_status)


    paginator = Paginator(postage_qs, 25)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/postage/history.html', {'page_obj': queryset,
                                                                    'count': postage_qs.count()})

