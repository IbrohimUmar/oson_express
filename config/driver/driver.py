from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from order.models import Order
from store.models import Product
from user.models import User, Regions, Districts, CashierUser, CashCategory, TempPayment
from django.contrib.auth.decorators import permission_required
from config.cash.crud import cash_in_create, cash_out_create

from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import F
import datetime
from cash.models import Cash
from asgiref.sync import async_to_sync, sync_to_async

from user.models import DriverUser
from django.shortcuts import get_object_or_404

@login_required(login_url='/login')
@permission_required('admin.driver_list', login_url="/home")
def driver_list(request):
    driver = User.objects.filter(type=2).order_by('-is_active')
    return render(request, 'driver/list.html', {"driver":driver})



@login_required(login_url='/login')
@permission_required('admin.driver_temp_payment_list', login_url="/home")
def driver_temp_payment_list(request):
    def get_or_null(obj):
        if obj:
            return obj.id
        return 0
    temp_payment = TempPayment.objects.all().order_by("-created_at")
    if request.method == 'POST':
        r = request.POST
        type = r.get("type", None)

        if type == "check":
            query = get_object_or_404(TempPayment, id=r['temp_id'])
            if query.cashier is not None:
                try:
                    cash_in_create(request.user, query.user.id, get_or_null(query.cashier), query.amount, get_or_null(query.category), query.desc)
                except IntegrityError as e:
                    messages.error(request, e)
            else:
                try:
                    cash_out_create(request.user, query.user.id, get_or_null(query.cashier), query.amount, get_or_null(query.category), query.desc)
                except IntegrityError as e:
                    messages.error(request, e)
            query.delete()
            messages.success(request, "Tasdiqlandi")
        elif type == "delete":
            query = get_object_or_404(TempPayment, id=r['temp_id'])
            query.delete()
            messages.success(request, "O'chirildi")
        elif type == "cancel":
            query = get_object_or_404(TempPayment, id=r['temp_id'])
            query.desc = r['desc']
            query.status = 2
            query.save()
            messages.success(request, "Bekor qilindi")
        return redirect("driver_temp_payment_list")
    paginator = Paginator(temp_payment, 100)
    page_number = request.GET.get('page')
    order = paginator.get_page(page_number)
    return render(request, 'driver/temp_payment_list.html', {"queryset":order})
    


from .daily_report import calculate_sales_percentage
from django.db.models import Count, Q
from django.utils import timezone

@login_required(login_url='/login')
@permission_required('admin.driver_date_by_statistic', login_url="/home")
def driver_date_by_statistic(request):
    now = timezone.now()
    from_date = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    to_date = request.GET.get("to_date", now.strftime("%Y-%m-%d"))

    driver = User.objects.filter(type=2, is_active=True).order_by("region_id").annotate(
        selling_count=Count('order', filter=Q(order__status=4,order__updated_at__date__range=(from_date, to_date))),
        cancelled_count=Count('order', filter=Q(order__status=5,order__updated_at__date__range=(from_date, to_date))),
        send_product_count=Count('order', filter=Q(order__driver_shipping_start_date__range=(from_date, to_date))),
        call_back_count=Count('order', filter=Q(order__status=6,order__updated_at__date__range=(from_date, to_date))),
        being_delivery_count=Count('order', filter=Q(order__status=3,order__updated_at__date__range=(from_date, to_date))),
        total_changed_order=(F("selling_count")+F("cancelled_count"))
    ).values('first_name', 'id',  'username', 'region__name','last_name','selling_count', 'cancelled_count', 'send_product_count', 'call_back_count', 'being_delivery_count', 'total_changed_order')
    for d in driver:
        d['sales_interest'] = calculate_sales_percentage(d['selling_count'], d['total_changed_order'])
        
    total_results = {'selling_count':0, 'cancelled_count':0, 'send_product_count':0, 'call_back_count':0, 'being_delivery_count':0, 'total_changed_order':0}
    for d in driver:
        total_results['selling_count'] += d['selling_count']
        total_results['cancelled_count'] += d['cancelled_count']
        total_results['send_product_count'] += d['send_product_count']
        total_results['call_back_count'] += d['call_back_count']
        total_results['being_delivery_count'] += d['call_back_count']
        total_results['total_changed_order'] += d['total_changed_order']
    total_results['sales_interest'] = calculate_sales_percentage(total_results['selling_count'], total_results['total_changed_order'])
        
    driver = sorted(driver, key=lambda d: float(d['sales_interest']), reverse=True)
    return render(request, 'driver/date_by_statistic.html', {"driver":driver, 'now':now.strftime("%Y-%m-%d"), 'total_results':total_results})


@login_required(login_url='/login')
@permission_required('admin.driver_date_by_statistic', login_url="/home")
def driver_date_by_district_statistic(request, driver_id):
    driver = get_object_or_404(User, id=driver_id, type=2)
    now = timezone.now()
    from_date = request.GET.get("from_date", now.strftime("%Y-%m-%d"))
    to_date = request.GET.get("to_date", now.strftime("%Y-%m-%d"))
    district_statistic = []
    for i in driver.allow_districts.all():
        order = Order.objects.filter(driver_id=driver_id, customer_district_id=i.id).aggregate(
            selling_count=Count('id', filter=Q(status=4, updated_at__date__range=(from_date, to_date))),
            cancelled_count=Count('id', filter=Q(status=5, updated_at__date__range=(from_date, to_date))),
            send_product_count=Count('id', filter=Q(driver_shipping_start_date__range=(from_date, to_date))),
            call_back_count=Count('id', filter=Q(status=6, updated_at__date__range=(from_date, to_date))),
            being_delivery_count=Count('id', filter=Q(status=3, updated_at__date__range=(from_date, to_date))),
        )
        total_changed_order = order['selling_count'] + order['cancelled_count']
        order['sales_interest'] = calculate_sales_percentage(order['selling_count'], total_changed_order)
        order['district_name'] = i.name
        district_statistic.append(order)
    district_statistic = sorted(district_statistic, key=lambda d: float(d['sales_interest']), reverse=True)
    return render(request, 'driver/date_by_district_statistic.html', {"driver":driver, 'district_statistic':district_statistic,'now':now.strftime("%Y-%m-%d")})





@login_required(login_url='/login')
@permission_required('admin.driver_list_statistic', login_url="/home")
def driver_list_statistic(request):
    driver = User.objects.filter(type=2)
    return render(request, 'driver/list_statistic.html', {"driver":driver})


from django.contrib.auth.hashers import make_password

@login_required(login_url='/login')
@permission_required('admin.driver_create', login_url="/home")
def driver_create(request):
    def get_or_null(value):
        if value:
            return value
        return 0
    region = Regions.objects.all()
    district = Districts.objects.all()
    if request.method == "POST":
        r = request.POST
        print(request.POST)
        if len(r['password_text'])<8:
            return render(request, 'driver/create.html', {"r": request.POST, 'messages_error':"Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})
        if User.objects.filter(username=int(r['phone'])).exists():
            return render(request, 'driver/create.html', {"r": request.POST, 'messages_error':"Bu telefon raqamli foydalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})
        driver=User.objects.create(
            username=int(r['phone']), first_name=r['first_name'], last_name=r['last_name'],
            password=make_password(r['password_text']), password_text=r['password_text'],
            type=2,
            is_active={"on":True}.get(r.get("is_active", False), False),
            fee_is_special={"on":True}.get(r.get("special_fee", False), False),
            special_fee_amount=int(get_or_null(r.get('special_fee_amount', 0))),
                        region_id=r['region'],
            district_id=r['district']
        )
        messages.success(request, "Haydovchi qo'shildi")
        return redirect("driver_list")
    return render(request, 'driver/create.html', {"region":region, "district":district})


@login_required(login_url='/login')
@permission_required('admin.driver_edit', login_url="/home")
def driver_edit(request, id):
    def get_or_null(value):
        if value:
            return value
        return 0
    driver = get_object_or_404(User, id=id, type=2)
    district = Districts.objects.filter(region_id=driver.region_id)

    cashier_list = CashierUser.objects.all()
    if request.method == "POST":
        r = request.POST
        if len(r['password_text'])<8:
            return render(request, 'driver/edit.html', {"district":district, "r": driver, 'messages_error':"Parol uzunligi kamida 8 tadan ko'p bo'lishi kerak. xafsizlik yuzasidan"})
        if int(r['username']) != int(driver.username):
            if User.objects.filter(username=int(r['username'])).exists():
                return render(request, 'driver/edit.html', {"district":district,"r":  driver, 'messages_error':"Bu telefon raqamli foydalanuvchi mavjud. iltimos boshqa telefon raqam kiriting"})
        driver=User.objects.filter(id=id).update(
            username=int(r['username']), first_name=r['first_name'], last_name=r['last_name'],
            password=make_password(r['password_text']), password_text=r['password_text'],
            type=2,
            is_active={"on":True}.get(r.get("is_active", False), False),
            fee_is_special={"on":True}.get(r.get("fee_is_special", False), False),
            special_fee_amount=int(get_or_null(r.get('special_fee_amount', 0))),
            district_id=r['district']
        )
        districts = None
        if r.get('allow_districts', None):
            districts = Districts.objects.filter(id__in=dict(r)['allow_districts'])
        drivers = User.objects.get(id=id)
        if districts:
            drivers.allow_districts.clear()
            drivers.allow_districts.add(*districts)
        else:
            drivers = drivers.allow_districts.clear()
            
        cashier_list = None
        if r.get('allowed_cashier', None):
            cashier_list = User.objects.filter(id__in=dict(r)['allowed_cashier'])

        item, create = DriverUser.objects.get_or_create(user_id=id)
        if cashier_list:
            item.allowed_cashier.clear()
            item.allowed_cashier.add(*cashier_list)
        else:
            item = item.allowed_cashier.clear()
        messages.success(request, "O'zgartirildi")
        return redirect("driver_edit", id)
    return render(request, 'driver/edit.html', {'r':driver, "district":district, 'cashier_list':cashier_list})





from config.export_excel import export_excel_from_driver_order_history


import threading


@login_required(login_url='/login')
@permission_required('admin.driver_about', login_url="/home")
def driver_about(request, id):
    driver = User.objects.filter(id=id, type=2).first()
    if driver:
        return render(request, 'driver/details.html', {"d":driver})
    return redirect('driver_list')


