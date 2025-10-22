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
@permission_required('cash.cash_list', login_url="/home")
def cash(request):
    return render(request, 'cash/main.html')


@login_required(login_url='/login')
@permission_required('cash.cash_list', login_url="/home")
def cash_json_data(request):
    user = request.user
    g = request.GET
    if user.is_superuser:
        data = Cash.objects.filter(person_type='1').order_by("-created_at")
    else:
        data = Cash.objects.filter(Q(from_user=user) | Q(to_user=user), person_type='1').order_by("-created_at")

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
@permission_required('cash.cash_list', login_url="/home")
def cash_report_json_data(request):
    if request.user.is_superuser:
        cash_list = CashierUser.objects.exclude(user__type='6').values("user_id", "balance", "user__first_name", "user__last_name")
        total_balance = cash_list.aggregate(t=Coalesce(Sum("balance"), 0))["t"]

    else:
        # cash_list = CashierUser.objects.filter().values("balance", "user__first_name", "user__last_name")
        cash_list = []
        total_balance = request.user.cashieruser.balance
    return JsonResponse({"cash_list": list(cash_list),
                         "total_balance": total_balance})


@login_required(login_url='/login')
@permission_required('cash.cash_list', login_url="/home")
def cash_filter_json_data(request):
    user_list = User.objects.filter(type__in=['1', '2', '6'], is_active=True).values("id", "first_name", "last_name", "username", "type")
    category = CashCategory.objects.filter(for_who='1').values("id", "name")
    # if request.user.is_superuser:
    #     user_list = User.objects.filter(is_active=True).values("id", "first_name", "last_name",
    #                                                                           "username", "type")
    #     category = CashCategory.objects.all().values("id", "name")

    # else:
    #     user_list = User.objects.filter(type__in=request.user.cash_allowed_payment_types.all().values_list("id", flat=True), cashier=True, is_active=True).values("id",
    #                                                                                                     "first_name",
    #                                                                                                     "last_name",
    #                                                                                                     "username",
    #                                                                                                     "type")
    #     category = CashCategory.objects.filter(
    #             id__in=list(request.user.cash_category.all().values_list("id", flat=True))).values("id", "name")
    return JsonResponse({'data': {"user_list": list(user_list),
                                  "category": list(category)}})


@login_required(login_url='/login')
@permission_required('cash.cash_in', login_url="/home")
def cash_in_data_json(request):
    if request.method == "GET":
        from_user_list = User.objects.filter(type='2', is_active=True).values("id", "first_name", "last_name",
                                                                              "username", "type")
        if request.user.is_superuser:
            to_user_list = User.objects.filter(cashier=True, is_active=True).values("id", "first_name", "last_name",
                                                                                    "username", "type")
            category = CashCategory.objects.all().values("id", "name")
        else:
            to_user_list = User.objects.filter(id=request.user.id, cashier=True, is_active=True).values("id",
                                                                                                        "first_name",
                                                                                                        "last_name",
                                                                                                        "username",
                                                                                                        "type")
            category = CashCategory.objects.filter(
                for_who='1',
                id__in=list(request.user.cashieruser.cash_category.all().values_list("id", flat=True))).values("id",
                                                                                                               "name")
        return JsonResponse({'data': {"from_user_data": list(from_user_list),
                                      "to_user_list": list(to_user_list),
                                      "category": list(category)}})
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        data = body['data']
        data_amount = int(data['amount'].replace(",", ""))
        try:
            with transaction.atomic():
                category = None
                if int(data['category']) != 0:
                    category = CashCategory.objects.get(id=int(data['category']))
                CashierUser.objects.filter(user_id=data['to_user']).update(balance=F("balance") + data_amount,
                                                                           updated_at=datetime.datetime.now())
                cash = Cash.objects.create(type=1, from_user_id=data['from_user'],
                                           to_user_id=data["to_user"],
                                           responsible=request.user,
                                           amount=data_amount,
                                           category=category,
                                           desc=data['desc'],
                                           )
                return JsonResponse({'status': 200, "message": "created"})

        except IntegrityError as e:
            handle_exception(e)
            return JsonResponse({'status': 404, "message": e})


@login_required(login_url='/login')
@permission_required('cash.cash_transfer', login_url="/home")
def cash_transfer_data_json(request):
    if request.method == "GET":
        if request.user.is_superuser:
            cashier_list = User.objects.filter(cashier=True, is_active=True).values("id", "first_name", "last_name",
                                                                                    "username", "type")

        else:
            cashier_list = User.objects.filter(cashier=True, is_active=True,
                                               type__in=request.user.cashieruser.cash_allowed_payment_types.all().values_list(
                                                   "id", flat=True)).values("id", "first_name", "last_name",
                                                                            "username", "type")

        return JsonResponse({'data': {"cashier_list": list(cashier_list)}})
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        data = body['data']
        data_amount = int(data['amount'].replace(",", ""))
        try:
            with transaction.atomic():
                CashierUser.objects.filter(user_id=data['from_user']).update(balance=F("balance") - data_amount,
                                                                             updated_at=datetime.datetime.now())
                CashierUser.objects.filter(user_id=data['to_user']).update(balance=F("balance") + data_amount,
                                                                           updated_at=datetime.datetime.now())

                cash = Cash.objects.create(type=3,
                                           from_user_id=data['from_user'],
                                           to_user_id=data["to_user"],
                                           responsible=request.user,
                                           amount=data_amount,
                                           desc=data['desc'],
                                           )
                return JsonResponse({'status': 200, "message": "created"})
        except IntegrityError as e:
            handle_exception(e)
            return JsonResponse({'status': 404, "message": e})


# qabul qiluvchi bazida bo'lmaslik

@login_required(login_url='/login')
@permission_required('cash.cash_out', login_url="/home")
def cash_out_data_json(request):
    if request.method == "GET":
        user = request.user
        if user.is_superuser:
            from_user_list = User.objects.filter(cashier=True, is_active=True).values("id", "first_name", "last_name",
                                                                                      "username", "type")
            to_user_list = User.objects.filter(cashier=False, is_active=True, type=6).values("id", "first_name",
                                                                                             "last_name",
                                                                                             "username", "type")
            category = CashCategory.objects.filter(for_who='1').values("id", "name")


        else:
            from_user_list = User.objects.filter(id=user.id, cashier=True, is_active=True).values("id", "first_name",
                                                                                                  "last_name",
                                                                                                  "username", "type")
            to_user_list = User.objects.filter(
                type__in=user.cashieruser.cash_allowed_payment_types.all().values_list("id", flat=True),
                cashier=False, is_active=True).values("id", "first_name", "last_name",
                                                      "username", "type")
            category = CashCategory.objects.filter(for_who='1',
                id__in=user.cashieruser.cash_category.all().values_list("id", flat=True)).values("id", "name")

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
                    to_user = User.objects.get(id=int(data['to_user']))
                    CashierUser.objects.filter(user_id=data.get('to_user', 0)).update(
                        balance=F("balance") + data_amount,
                        updated_at=datetime.datetime.now())
                CashierUser.objects.filter(user_id=data['from_user']).update(balance=F("balance") - data_amount,
                                                                             updated_at=datetime.datetime.now())

                cash = Cash.objects.create(type=2,
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


