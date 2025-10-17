import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from order.models import Order
from postage.models import Postage, LogisticBranch, PostageDetails
from services.handle_exception import handle_exception

from user.models import Regions, User


@login_required(login_url='/login')
def postage_branch_driver_history(request, logistic_branch_id):
    logistic_branch = get_object_or_404(LogisticBranch, id=logistic_branch_id)
    logistic_branch.perms = logistic_branch.get_user_permission(request.user)
    drivers = User.objects.filter(type='2')
    postage_qs = Postage.objects.filter(Q(from_logistic_branch=logistic_branch) | Q(to_logistic_branch=logistic_branch), action__in=['3', '4']).order_by("-id")
    driver = request.GET.get("driver", '0')
    if driver != '0':
        postage_qs = postage_qs.filter(Q(from_user_id=driver)|Q(to_user_id=driver))

    action = request.GET.get("action", '0')
    if action != '0':
        postage_qs = postage_qs.filter(action=action)

    from_user_status = request.GET.get("from_user_status", '0')
    if from_user_status != '0':
        postage_qs = postage_qs.filter(from_user_status=from_user_status)

    to_user_status = request.GET.get("to_user_status", '0')
    if to_user_status != '0':
        postage_qs = postage_qs.filter(to_user_status=to_user_status)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                '''
                haydovchiga pochta chiqim qilish yoki pochta qaytarish
                yoki chiqarilmoqchi bo'lingan chiqim haydovchidan bekor qilinsa qaytarib olinsa
                
                '''
                action = request.POST['action']
                postage = Postage.objects.filter(Q(from_logistic_branch=logistic_branch) | Q(to_logistic_branch=logistic_branch),
                                                 action__in=['3', '4'],
                                                 id=request.POST.get('postage_id', 0)).first()
                if not postage:
                    messages.error(request, "Bunday pochta mavjud emas")
                    return redirect('postage_branch_driver_history', logistic_branch_id)

                if postage.action == '3' and action == 'confirm':     # pochta haydovchiga chiqim tasdiqlansa
                    if postage.from_user_status != '1':
                        messages.error(request, "Pochtani holatini o'zgartirish mumkun emas")
                        return redirect('postage_branch_driver_history', logistic_branch_id)

                    postage.from_user_status='2'
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.from_user = request.user
                    postage.save()
                    messages.success(request, "Tasdiqlandi")
                    return redirect('postage_branch_driver_history', logistic_branch_id)


                if postage.action == '3' and action == 'cancel':    # pochta haydovchiga chiqim bekor qilinsa
                    if postage.from_user_status != '1':
                        messages.error(request, "Pochtani holatini o'zgartirish mumkun emas")
                        return redirect('postage_branch_driver_history', logistic_branch_id)

                    postage.from_user_status = '3'
                    postage.from_user = request.user
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()

                    orders = postage.postage_orders
                    orders.update(transaction_lock=False)
                    messages.success(request, "Qaytarildi")
                    return redirect('postage_branch_driver_history', logistic_branch_id)


                if postage.action == '3' and action == 'cancel_because_to_user_cancel':    # chiqim tasdiqlangan lekin haydovchi bekor qilsa
                    if postage.to_user_status != '3' or postage.from_user_status != '2':
                        messages.error(request, "Pochtani holatini o'zgartirish mumkun emas")
                        return redirect('postage_branch_driver_history', logistic_branch_id)

                    postage.from_user_status = '3'
                    postage.from_user = request.user
                    postage.from_user_status_changed_at = datetime.datetime.now()
                    postage.save()

                    orders = postage.postage_orders
                    orders.update(transaction_lock=False,
                                  logistic_branch_id=logistic_branch_id)
                    messages.success(request, "Qaytarildi")
                    return redirect('postage_branch_driver_history', logistic_branch_id)
                messages.error(request, "Action aniq emas")
                return redirect('postage_branch_driver_history', logistic_branch_id)

        except Exception as e:
            handle_exception(e)
            messages.error(request, f"Hatolik yuz berdi {e}")
            return redirect('postage_branch_driver_history')

    '''
    buyerda filealdan chiqgan yoki qaytib kelgan amaliyotlar ro'yxati bo'ladi
    
    buyerdan fileal tasdiqlariham bo'lishi kerak pochta qabul qilish ni tasdiqlash
    yoki pochta yuborishni tasdiqlash

    1. agar seller pochta topshirishni boshlagan bo'lsa 
    amaliyotni seller boshlaydi
    ichida harbir pochtani skannerlab olish imkoniyati bo'lishi kerak
    va hammasi tasdiqlanganidan keyin tasdiqlash knopkasi ko'rinishi kerak

    '''
    paginator = Paginator(postage_qs, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'postage/branch/driver/history.html', {"logistic_branch": logistic_branch,
                                                                  'page_obj': queryset,
                                                                  'drivers': drivers,
                                                                  'count': postage_qs.count(),
                                                                  })