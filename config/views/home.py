from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum, Case, When, IntegerField
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from order.models import Order
from user.models import User

from datetime import date, timedelta


def development(request):
    '''
    muammo bo'liyotgan postagelarni olish va orderlarni qabul qilindiga o'tkazish kerak
    '''
    from order.models import Order, SellerOperatorStatusDesc
    # user = User.objects.filter(username=998332236969)
    # print(user)
    # orders = Order.objects.filter(seller__username=998332236969, status=6)
    # orders = Order.objects.filter(seller__username=998332236969, status=9, operator__isnull=False).update(status=6)
    # print(orders.count())
    # print('budi')
    from config.seller_app.orders.edit import allow_edit_seller_status
    # order = Order.objects.filter(status='3')
    # for o in order:
    #     o.update_driver_fee()
    #     o.update_logistic_fee()
    # orders = Order.objects.filter(status__in=allow_edit_seller_status, operator_note__isnull=False)
    # orders = Order.objects.filter(status__in=[7,8, 2, 13, 3, 4, 5,14, 15], total_product_input_price=0)
    # # orders = Order.objects.filter(id=696)
    # for o in orders:
    #     o.update_total_input_price()
    #     print(o.get_status_display(), o.id)
    # print(orders)
    # t = orders.count()
    # for i in orders:
    #     t -= 1
    #     # print(i.operator_comment)
    #     description = SellerOperatorStatusDesc.objects.filter(seller=i.seller, description=i.operator_note).first()
    #     if description:
    #         i.operator_comment = description
    #         i.save()
    #         print('topildi', i.id)
    #     print(t)

    # import datetime
    # from order.models import Order
    # from postage.models import Postage, PostageDetails
    # postage = Postage.objects.filter(id__in=[67])
    # for p in postage:
    #     postage_details = PostageDetails.objects.filter(postage=p)
    #     p.from_user_status = '2'
    #     p.from_user_status_changed_at = datetime.datetime.now()
    #     p.to_user_status = '2'
    #     p.to_user_status_changed_at = datetime.datetime.now()
    #     p.save()
    #     Order.objects.filter(
    #         id__in=list(postage_details.values_list('order_id', flat=True))
    #     ).update(status='13', logistic_branch_id=1, transaction_lock=False)
    #     postage_details.update(scan_from_user=True, scan_to_user=True)

    # order = Order.objects.get(id=681)
    # order.update_driver_fee()
    # order.update_logistic_fee()
    # print(order.driver_fee)
    return JsonResponse({"status":200}, safe=False)


@login_required(login_url='/login')
def home(request):
    if request.user.type == "2":
        messages.success(request, "Xush kelibsiz")
        return redirect("driver_app_profile")
    if request.user.type == "4":
        messages.success(request, "Xush kelibsiz")
        return redirect("marketer_app_profile")
    if request.user.type == "3":
        messages.success(request, "Xush kelibsiz")
        return redirect("operator_app_profile")
    if request.user.type == "6":
        messages.success(request, "Xush kelibsiz")
        return redirect("seller_app_home")

    sync_permission = request.GET.get("sync_permission")
    if sync_permission and request.user.is_superuser:
        from config.permission import sync_permission
        sync_permission()
        messages.success(request, "Sinxronlandi")
        return redirect("home")

    from django.db.models import Sum, Case, When, IntegerField, Q


    user_stat = User.objects.aggregate(
        driver_count=Count('id', filter=Q(type='2')),
        seller_count=Count('id', filter=Q(type='6')),
        marketer_count=Count('id', filter=Q(type='4')),
        operator_count=Count('id', filter=Q(type='3')),
    )
    order_stats = Order.objects.aggregate(
        filealdagi_pochta=Sum(
            Case(When(status="13", then=1), default=0, output_field=IntegerField())
        ),
        yetkazilayotgan=Sum(
            Case(When(status="3", then=1), default=0, output_field=IntegerField())
        ),
        yetkazilgan=Sum(
            Case(When(status="4", then=1), default=0, output_field=IntegerField())
        ),
        bekor_haydovchi=Sum(
            Case(When(status="5", then=1), default=0, output_field=IntegerField())
        ),
        bekor_filealda=Sum(
            Case(When(status="14", then=1), default=0, output_field=IntegerField())
        ),
        bekor_seller=Sum(
            Case(When(status="15", then=1), default=0, output_field=IntegerField())
        ),
    )

    # Hafta kunlari o'zbekcha ro'yxati
    uzbek_weekdays = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    today = date.today()
    last_3_days = [today - timedelta(days=i) for i in range(2, -1, -1)]
    date_labels = [
        {
            "weekday": uzbek_weekdays[d.weekday()],  # Python weekday() 0=Dushanba ... 6=Yakshanba
            "date": d.strftime("%d-%b")  # 22-Dec kabi, kerak bo'lsa %d-%m format ham qilsa bo'ladi
        }
        for d in last_3_days
    ]

    last_3_days_stats = Order.objects.aggregate(
        # 1. Uch kun ichida kelgan lidlar
        lead_day0=Count('id', filter=Q(created_at__date=last_3_days[2])),
        lead_day1=Count('id', filter=Q(created_at__date=last_3_days[1])),
        lead_day2=Count('id', filter=Q(created_at__date=last_3_days[0])),

        sold_day0=Count('id', filter=Q(status="4", driver_status_changed_at__date=last_3_days[2])),
        sold_day1=Count('id', filter=Q(status="4", driver_status_changed_at__date=last_3_days[1])),
        sold_day2=Count('id', filter=Q(status="4", driver_status_changed_at__date=last_3_days[0])),

        shipped_day0=Count('id', filter=Q(status__in=["3", "4", "5", "14", "15"], driver_shipping_start_date=last_3_days[2])),
        shipped_day1=Count('id', filter=Q(status__in=["3", "4", "5", "14", "15"], driver_shipping_start_date=last_3_days[1])),
        shipped_day2=Count('id', filter=Q(status__in=["3", "4", "5", "14", "15"], driver_shipping_start_date=last_3_days[0])),
    )
    print(last_3_days_stats)

    return render(request, 'home/index.html', {
        "user_stat":user_stat,
        "order_stat":order_stats,
        "date_labels":date_labels,
        "last_3_days_stats":last_3_days_stats,
    })


@login_required(login_url='/login')
def change_color(request):
    user = User.objects.get(id=request.user.id)
    if user.theme == '1':
        change(user, '2')
    elif user.theme == '2' or user.theme == None:
        change(user, '1')
    return JsonResponse({'status': "true"})


def change(user, type):
    user.theme = type
    user.save()


def my_custom_page_not_found_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '404 page not found'})


def my_custom_error_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '500 server error'})


def my_custom_permission_denied_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '403 peremission denied'})


def my_custom_bad_request_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '400 bad request'})
