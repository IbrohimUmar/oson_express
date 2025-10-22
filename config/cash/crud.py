from django.db import transaction, IntegrityError
from django.db.models import F, Sum
import datetime

from services.handle_exception import handle_exception
from user.models import CashierUser, User, CashCategory
from cash.models import Cash
from django.db.models.functions import Coalesce



def cash_in_create(responsible, from_user, to_user, amount, category, desc):
    try:
        with transaction.atomic():
            category_obj = None
            to_user_obj = None
            if int(category) != 0:
                category_obj = CashCategory.objects.get(id=int(category))
            if int(to_user) != 0:
                to_user_obj = User.objects.get(id=to_user)
            CashierUser.objects.filter(user_id=to_user).update(balance=F("balance") + int(amount),updated_at=datetime.datetime.now())
            CashierUser.objects.filter(user_id=from_user).update(balance=F("balance") - int(amount),updated_at=datetime.datetime.now())
            cash = Cash.objects.create(type=1,
                                       from_user_id=from_user,
                                       to_user=to_user_obj,
                                       responsible=responsible,
                                       amount=amount,
                                       category=category_obj,
                                       desc=desc,
                                       )
            return cash
    except IntegrityError as e:
        handle_exception(e)
        return e


def cash_out_create(responsible, from_user, to_user, amount, category, desc):
    try:
        with transaction.atomic():
            category_obj = None
            to_user_obj = None
            if int(category) != 0:
                category_obj = CashCategory.objects.get(id=int(category))
            if int(to_user) != 0:
                to_user_obj = User.objects.get(id=to_user)
            CashierUser.objects.filter(user_id=to_user).update(balance=F("balance") + int(amount),updated_at=datetime.datetime.now())
            CashierUser.objects.filter(user_id=from_user).update(balance=F("balance") - int(amount),updated_at=datetime.datetime.now())
            cash = Cash.objects.create(type=2,
                                       from_user_id=from_user,
                                       to_user=to_user_obj,
                                       responsible=responsible,
                                       amount=amount,
                                       category=category_obj,
                                       desc=desc,
                                       )
            return cash
    except IntegrityError as e:
        handle_exception(e)
        return e


def cashier_balance_update(cashier_id):
    cashier = CashierUser.objects.filter(user_id=cashier_id).first()
    if cashier:
        print(cashier.balance)

        total_in = Cash.objects.filter(to_user_id=cashier_id).aggregate(t=Coalesce(Sum("amount"),0))['t']
        total_out = Cash.objects.filter(from_user_id=cashier_id).aggregate(t=Coalesce(Sum("amount"),0))['t']
        cashier.balance=total_in-total_out
        cashier.save()