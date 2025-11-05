import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from cash.models import Cash
from config.cash.crud import check_paid_orders, cashier_balance_update, update_paid_orders
from services.handle_exception import handle_exception
from services.logs.log_helpers import log_create, log_update
from user.models import User, CashCategory, CashierUser, SystemLog
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

                cashier_old = CashierUser.objects.filter(user_id=data['to_user']).first()
                if data.get("to_user", None) or cashier_old:
                    CashierUser.objects.filter(user_id=data['to_user']).update(balance=F("balance") + data_amount,
                                                                               updated_at=datetime.datetime.now())
                cashier_new = CashierUser.objects.filter(user_id=data['to_user']).first()
                if cashier_old:
                    log_update(request, request.user, cashier_old, cashier_new, fields=['balance'], action_type='CashierUser_UPDATE_1')


                from_user = None
                if data.get('from_user', None):
                    from_user = User.objects.filter(id=data['from_user']).first()

                cash = Cash.objects.create(type=1, from_user_id=data['from_user'],
                                           to_user_id=data["to_user"],
                                           responsible=request.user,
                                           amount=data_amount,
                                           leave_amount=data_amount,
                                           category=category,
                                           desc=data['desc'],
                                           )
                log_create(request, request.user, cash, action_type='Cash_CREATE_1')

                if from_user and from_user.type == '2':
                    check_paid_orders(data['from_user'])
                return JsonResponse({'status': 200, "message": "created"})

        except IntegrityError as e:
            handle_exception(e)
            return JsonResponse({'status': 404, "message": e})




@login_required(login_url='/login')
@permission_required('cash.cash_in', login_url="/home")
def cash_in_edit_data_json(request):
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        if body['type'] == 'edit':
            try:
                with transaction.atomic():
                    cash = Cash.objects.filter(id=body['cash_id'], type='1').first()
                    data = body['data']
                    # cash = Cash.objects.filter(id=123132, type='1').first()
                    if not cash:
                        return JsonResponse({'status': 404, "message": "Bunday to'lov topilmadi"})

                    category = None
                    if int(data['category']) != 0:
                        category = CashCategory.objects.get(id=int(data['category']))

                    # CashierUser.objects.filter(user_id=data['to_user']).update(balance=F("balance") + data_amount,
                    #                                                                updated_at=datetime.datetime.now())

                    old_amount = cash.amount
                    new_amount = int(data['amount'])

                    if old_amount < new_amount:
                        diff = new_amount - old_amount
                        cash.leave_amount += diff
                    old_cash = Cash.objects.get(id=cash.id)

                    updated_cashier_balance = []

                    from_user = None
                    if data.get('from_user', None):
                        from_user = User.objects.filter(id=data['from_user']).first()

                    if cash.from_user:
                        updated_cashier_balance.append(cash.from_user.id)

                    if cash.to_user:
                        updated_cashier_balance.append(cash.to_user.id)

                    cash.from_user_id = data['from_user']
                    cash.to_user_id = data['to_user']
                    cash.responsible = request.user
                    cash.amount = data['amount']
                    cash.category = category
                    cash.desc = data['desc']
                    cash.save()

                    log_update(
                        request=request,
                        created_by_user=request.user,
                        old_instance=old_cash,
                        new_instance=cash,
                        fields=['from_user', 'to_user', 'amount', 'category', 'desc'],
                        action_type="Cash_EDIT_1",
                        path_url=request.path
                    )

                    if cash.from_user:
                        updated_cashier_balance.append(cash.from_user.id)

                    if cash.to_user:
                        updated_cashier_balance.append(cash.to_user.id)


                    if cash.from_user and cash.from_user.type == '2':
                        if old_amount > new_amount:
                            update_paid_orders(cash.id)
                            # check_paid_orders(cash.from_user.id)
                        else:
                            check_paid_orders(cash.from_user.id)
                    updated_cashier_balance = list(set(updated_cashier_balance))
                    for u in set(updated_cashier_balance):
                        cashier_balance_update(u)

                    return JsonResponse({'status': 200, "message": "o'zgartirildi"})


            except IntegrityError as e:
                handle_exception(e)
                return JsonResponse({'status': 404, "message": f"Xato : {e}"})
            except Exception as e:
                handle_exception(e)
                return JsonResponse({'status': 404, "message": f"Xato : {e}"})


        if body['type'] == 'edit_data':
            cash = Cash.objects.filter(id=body['cash_id'], type='1').first()
            if not cash:
                return JsonResponse({'status': 404, "message": "Bunday to'lov topilmadi"})
            user = request.user
            from_user = cash.from_user
            to_user = cash.to_user
            return JsonResponse({'data': {
                "cash_id": cash.id,
                "from_user": cash.from_user.id,
                "from_user_select_2": {"id": from_user.id, "first_name": from_user.first_name,
                                       "last_name": from_user.last_name, "username": str(from_user.username),
                                       "type": from_user.type},
                "to_user": cash.to_user.id if cash.to_user else '',
                "to_user_select_2": {"id": to_user.id, "first_name": to_user.first_name, "last_name": to_user.last_name,
                                     "username": str(to_user.username), "type": to_user.type} if cash.to_user else {},
                "category": cash.category.id,
                "category_select_2": {"id": cash.category.id, "name": cash.category.name},
                "amount": cash.amount,
                "desc": cash.desc}, 'status':200})
        return JsonResponse({'status': 200, "message": "created"})
    return JsonResponse({'status': 404, "message": 'only post allowed'})


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
                update_cashier = [data['from_user'], data['to_user']]
                cash = Cash.objects.create(type=3,
                                           from_user_id=data['from_user'],
                                           to_user_id=data["to_user"],
                                           responsible=request.user,
                                           amount=data_amount,
                                           leave_amount=data_amount,
                                           desc=data['desc'],
                                           )
                log_create(request, request.user, cash, action_type='Cash_CREATE_2')

                for u in set(update_cashier):
                    cashier_balance_update(u)

                return JsonResponse({'status': 200, "message": "created"})
        except IntegrityError as e:
            handle_exception(e)
            return JsonResponse({'status': 404, "message": e})







@login_required(login_url='/login')
@permission_required('cash.cash_out', login_url="/home")
def cash_transfer_edit_data_json(request):
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        if body['type'] == 'edit':
            cash_old = Cash.objects.filter(id=body['data']['cash_id'], type='3').first()
            cash = Cash.objects.filter(id=body['data']['cash_id'], type='3').first()
            data = body['data']
            if not cash:
                return JsonResponse({'status': 404, "message": "Bunday o'tkazma topilmadi"})

            updated_cashier_balance = []
            updated_cashier_balance.append(cash.from_user.id)
            updated_cashier_balance.append(cash.to_user.id)

            cash.from_user_id = data['from_user']
            cash.to_user_id = data['to_user']
            cash.responsible = request.user
            cash.amount = data['amount']
            cash.desc = data['desc']
            cash.save()

            log_update(request, request.user, cash_old, cash,
                       fields=['from_user', 'to_user', 'amount', 'category', 'desc'],
                       action_type='Cash_EDIT_2')

            updated_cashier_balance.append(cash.from_user.id)
            updated_cashier_balance.append(cash.to_user.id)

            updated_cashier_balance = list(set(updated_cashier_balance))
            for u in set(updated_cashier_balance):
                cashier_balance_update(u)


            return JsonResponse({'status': 200, "message": "o'zgartirildi"})


        if body['type'] == 'data':
            cash = Cash.objects.filter(id=body['cash_id'], type='3').first()
            # cash = Cash.objects.filter(id=123132, type='1').first()
            if not cash:
                return JsonResponse({'status': 404, "message": "Bunday to'lov topilmadi"})

            user = request.user
            from_user = cash.from_user
            to_user = cash.to_user
            return JsonResponse({'data': {
                "cash_id": cash.id,
                "from_user": cash.from_user.id,
                "from_user_select_2": {"id": from_user.id, "first_name": from_user.first_name,
                                       "last_name": from_user.last_name, "username": str(from_user.username),
                                       "type": from_user.type},
                "to_user": cash.to_user.id if cash.to_user else '',
                "to_user_select_2": {"id": to_user.id, "first_name": to_user.first_name, "last_name": to_user.last_name,
                                     "username": str(to_user.username), "type": to_user.type} if cash.to_user else {},
                "amount": cash.amount,
                "desc": cash.desc}, 'status':200})
        return JsonResponse({'status': 200, "message": "created"})
    return JsonResponse({'status': 404, "message": 'only post allowed'})






# qabul qiluvchi bazida bo'lmaslik

@login_required(login_url='/login')
@permission_required('cash.cash_out', login_url="/home")
def cash_out_data_json(request):
    if request.method == "GET":
        user = request.user
        if user.is_superuser:
            from_user_list = User.objects.filter(cashier=True, is_active=True).values("id", "first_name", "last_name", "username", "type")
            to_user_list = User.objects.filter(cashier=False, is_active=True, type=6).values("id", "first_name", "last_name", "username", "type")
            category = CashCategory.objects.filter(for_who='1').values("id", "name")

        else:
            from_user_list = User.objects.filter(id=user.id, cashier=True, is_active=True).values("id", "first_name", "last_name", "username", "type")
            to_user_list = User.objects.filter(
                type__in=user.cashieruser.cash_allowed_payment_types.all().values_list("id", flat=True),
                cashier=False, is_active=True).values("id", "first_name", "last_name", "username", "type")
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
                updated_cashier_balance = []

                data_amount = int(data['amount'].replace(",", ""))

                if int(data['category']) != 0:
                    category = CashCategory.objects.get(id=int(data['category']))

                if data.get("to_user", None):
                    to_user = User.objects.get(id=int(data['to_user']))
                    updated_cashier_balance.append(to_user.id)

                updated_cashier_balance.append(data['from_user'])


                cash = Cash.objects.create(type=2,
                                           from_user_id=data['from_user'],
                                           to_user=to_user,
                                           responsible=request.user,
                                           amount=data_amount,
                                           leave_amount=data_amount,
                                           category=category,
                                           desc=data['desc'],
                                           )
                log_create(request, request.user, cash, action_type='Cash_CREATE_3')

                updated_cashier_balance = list(set(updated_cashier_balance))
                for u in set(updated_cashier_balance):
                    cashier_balance_update(u)

                return JsonResponse({'status': 200, "message": "created"})
        except IntegrityError as e:
            handle_exception(e)
            return JsonResponse({'status': 404, "message": e})




@login_required(login_url='/login')
@permission_required('cash.cash_out', login_url="/home")
def cash_out_edit_data_json(request):

    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        # data = body['data']

        if body['type'] == 'edit':
            try:
                with transaction.atomic():
                    cash_old = Cash.objects.filter(id=body['cash_id'], type='2').first()
                    cash = Cash.objects.filter(id=body['cash_id'], type='2').first()
                    data = body['data']
                    if not cash:
                        return JsonResponse({'status': 404, "message": "Bunday to'lov topilmadi"})

                    category = None
                    if int(data['category']) != 0:
                        category = CashCategory.objects.get(id=int(data['category']))

                    updated_cashier_balance = []

                    from_user = None
                    if data.get('from_user', None):
                        from_user = User.objects.filter(id=data['from_user']).first()

                    if cash.from_user:
                        updated_cashier_balance.append(cash.from_user.id)

                    cash.from_user = from_user
                    cash.to_user_id = data['to_user']
                    cash.responsible = request.user
                    cash.amount = data['amount']
                    cash.category = category
                    cash.desc = data['desc']
                    cash.save()

                    log_update(request, request.user, cash_old, cash,
                               fields=['from_user', 'to_user', 'amount', 'category', 'desc'],
                               action_type='Cash_EDIT_3')

                    if cash.from_user:
                        updated_cashier_balance.append(cash.from_user.id)

                    updated_cashier_balance = list(set(updated_cashier_balance))
                    for u in set(updated_cashier_balance):
                        cashier_balance_update(u)
                    return JsonResponse({'status': 200, "message": "o'zgartirildi"})

            except IntegrityError as e:
                handle_exception(e)
                return JsonResponse({'status': 404, "message": e})

        if body['type'] == 'data':
            cash = Cash.objects.filter(id=body['cash_id'], type='2').first()
            # cash = Cash.objects.filter(id=123132, type='1').first()
            if not cash:
                return JsonResponse({'status': 404, "message": "Bunday to'lov topilmadi"})

            user = request.user
            from_user = cash.from_user
            to_user = cash.to_user
            return JsonResponse({'data': {
                "cash_id": cash.id,
                "from_user": cash.from_user.id,
                "from_user_select_2": {"id": from_user.id, "first_name": from_user.first_name,
                                       "last_name": from_user.last_name, "username": str(from_user.username),
                                       "type": from_user.type},
                "to_user": cash.to_user.id if cash.to_user else '',
                "to_user_select_2": {"id": to_user.id, "first_name": to_user.first_name, "last_name": to_user.last_name,
                                     "username": str(to_user.username), "type": to_user.type} if cash.to_user else {},
                "category": cash.category.id,
                "category_select_2": {"id": cash.category.id, "name": cash.category.name},
                "amount": cash.amount,
                "desc": cash.desc}, 'status':200})
        return JsonResponse({'status': 200, "message": "created"})
        # except IntegrityError as e:
        #     handle_exception(e)
        #     return JsonResponse({'status': 404, "message": e})
    return JsonResponse({'status': 404, "message": 'only post allowed'})

