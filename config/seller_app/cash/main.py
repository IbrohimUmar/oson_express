import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from cash.models import Cash
from services.handle_exception import handle_exception
from user.models import User, CashCategory, CashierUser
from django.db import transaction, IntegrityError
from django.db.models import F
import json
from django.db.models import Sum
from django.db.models.functions import Coalesce


@login_required(login_url='/login')
@permission_required('admin.seller_app_cash_main', login_url="/home")
def seller_app_cash_main(request):
    return render(request, 'seller_app/cash/main.html')


@login_required(login_url='/login')
@permission_required('admin.seller_app_cash_main', login_url="/home")
def seller_app_cash_json_data(request):
    user = request.user
    g = request.GET
    data = Cash.objects.filter(Q(from_user=user) | Q(to_user=user)).order_by("-created_at")

    if request.GET.get("search", None):
        data = data.filter(desc__contains=g["search"])

    if request.GET.get("type", None):
        data = data.filter(type=g["type"])

    if request.GET.get("category", None):
        data = data.filter(category_id=g["category"])

    if request.GET.get("user", None):
        # data = data.filter(Q(from_user_id=g["user"])|Q(to_user_id=g["user"])|Q(responsible_id=g["user"]))
        data = data.filter(Q(from_user_id=g["user"]) | Q(to_user_id=g["user"]))

    if request.GET.get("from_date", None) and request.GET.get("to_date", None):
        data = data.filter(created_at__date__range=(g["from_date"], g["to_date"]))

    paginator = Paginator(data, request.GET.get('page_size', 50))
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    return JsonResponse({'data': list(page.object_list.values(
        "id", "type", "from_user_id", "from_user__first_name", "from_user__last_name", "from_user__username",
        "to_user_id", "to_user__first_name", "to_user__last_name", "to_user__username",
        "responsible_id", "responsible__first_name", "responsible__last_name", "responsible__username",
        "category_id", "category__name", "amount", "desc", "created_at__date", "created_at__time", "created_at",
        "updated_at")),

        "cash_total_amount": data.aggregate(t=Coalesce(Sum("amount"), 0))['t'],

        'total_item': data.count(),
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'number': page.number,
        'num_pages': paginator.num_pages,

    })


@login_required(login_url='/login')
@permission_required('admin.seller_app_cash_main', login_url="/home")
def seller_app_cash_report_json_data(request):
    cash_list = CashierUser.objects.filter(user=request.user).values("user_id", "balance", "user__first_name",
                                                                     "user__last_name")
    print(cash_list)
    print('cash_list')
    total_balance = cash_list.aggregate(t=Coalesce(Sum("balance"), 0))["t"]
    return JsonResponse({"cash_list": list(cash_list),
                         "total_balance": total_balance})


@login_required(login_url='/login')
@permission_required('admin.seller_app_cash_list', login_url="/home")
def seller_app_cash_filter_json_data(request):
    user_list = User.objects.filter(is_active=True, seller=request.user).values("id", "first_name", "last_name", "username", "type")
    category = CashCategory.objects.filter(Q(seller=None)| Q(seller=request.user), for_who='2').values("id", "name")
    return JsonResponse({'data': {"user_list": list(user_list),
                                  "category": list(category)}})

# qabul qiluvchi bazida bo'lmaslik



@login_required(login_url='/login')
@permission_required('admin.seller_app_cash_out_edit', login_url="/home")
def seller_app_cash_out_edit_data_json(request):
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        print('get_data', body)
        if body['type'] == 'get_data':
            cash = Cash.objects.filter(id=body['cash_id'], person_type='2', from_user=request.user, type='2').first()
            if not cash:
                return JsonResponse({'status': 404, "message": "Bunday to'lov mavjud emas"})
            user = request.user
            from_user = cash.from_user
            to_user = cash.to_user
            return JsonResponse({'data': {
                "cash_id": cash.id,
                "from_user": cash.from_user.id,
                "from_user_select_2": { "id": from_user.id, "first_name": from_user.first_name, "last_name": from_user.last_name, "username": str(from_user.username), "type": from_user.type },
                "to_user": cash.to_user.id if cash.to_user else '',
                "to_user_select_2": { "id": to_user.id, "first_name": to_user.first_name, "last_name": to_user.last_name, "username": str(to_user.username), "type": to_user.type } if cash.to_user else {},
                "category": cash.category.id,
                "category_select_2": {"id":cash.category.id, "name":cash.category.name},
                "amount": cash.amount,
                "desc": cash.desc}})

        elif body['type'] == 'edit':

            try:
                with transaction.atomic():
                    data = body['data']

                    cash = Cash.objects.filter(id=data['cash_id'], person_type='2', from_user=request.user, type='2').first()
                    if not cash:
                        return JsonResponse({'status': 404, "message": "Bunday to'lov mavjud emas"})

                    old_amount = cash.amount
                    new_amount = int(data['amount'])
                    diff = old_amount - new_amount  # 🔑 DİKKAT: yön ters olmalı

                    CashierUser.objects.filter(user=cash.from_user).update(
                        balance=F("balance") + diff,  # artı farkı doğrudan uygula
                        updated_at=datetime.datetime.now()
                    )
                    if data['to_user_select_2']:
                        cash.to_user_id = data['to_user_select_2']['id']
                    else:
                        cash.to_user_id = None
                    cash.category_id = data['category']
                    cash.amount = data['amount']
                    cash.desc = data['desc']
                    cash.save()
                    return JsonResponse({'status': 200, "message": "created"})

            except IntegrityError as e:
                handle_exception(e)
                return JsonResponse({'status': 404, "message": e})
            except Exception as e:
                handle_exception(e)
                return JsonResponse({'status': 404, "message": e})



@login_required(login_url='/login')
@permission_required('admin.seller_app_cash_out', login_url="/home")
def seller_app_cash_out_data_json(request):
    if request.method == "GET":
        user = request.user
        from_user_list = User.objects.filter(id=user.id, is_active=True).values("id", "first_name",
                                                                                              "last_name",
                                                                                           "username", "type")
        to_user_list = User.objects.filter(
            seller=request.user,
            cashier=False, is_active=True).values("id", "first_name", "last_name",
                                                  "username", "type")
        category = CashCategory.objects.filter(Q(seller=None) | Q(seller=request.user), for_who='2').values("id",
                                                                                                            "name")
        return JsonResponse({'data': {"from_user_data": list(from_user_list),
                                      "to_user_list": list(to_user_list),
                                      "category": list(category)}})
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        data = body['data']
        try:
            with transaction.atomic():
                category = None
                to_user = None

                data_amount = int(data['amount'].replace(",", ""))

                if int(data['category']) != 0:
                    category = CashCategory.objects.get(id=int(data['category']))

                if data.get("to_user", None):
                    to_user = User.objects.get(id=int(data['to_user']), seller=request.user)
                    CashierUser.objects.filter(user_id=data.get('to_user', 0)).update(
                        balance=F("balance") + data_amount,
                        updated_at=datetime.datetime.now())

                CashierUser.objects.filter(user_id=data['from_user']).update(
                    balance=F("balance") - data_amount, updated_at=datetime.datetime.now())

                cash = Cash.objects.create(
                                            person_type=2,
                                            type=2,
                                           from_user_id=data['from_user'],
                                           to_user=to_user,
                                           responsible=request.user,
                                           amount=data_amount,
                                           category=category,
                                           desc=data['desc'],
                                           )
                return JsonResponse({'status': 200, "message": "created"})
        except IntegrityError as e:
            handle_exception(e)
            return JsonResponse({'status': 404, "message": e})


