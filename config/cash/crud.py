from copy import deepcopy
from django.utils import timezone

from django.db import transaction, IntegrityError
from django.db.models import F, Sum
import datetime

from order.models import CashOrderRelation, Order
from services.handle_exception import handle_exception
from services.logs.log_helpers import log_update, log_create
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


            # CashierUser.objects.filter(user_id=to_user).update(balance=F("balance") + int(amount),updated_at=datetime.datetime.now())
            # CashierUser.objects.filter(user_id=from_user).update(balance=F("balance") - int(amount),updated_at=datetime.datetime.now())
            cash = Cash.objects.create(type=1,
                                       from_user_id=from_user,
                                       to_user=to_user_obj,
                                       responsible=responsible,
                                       amount=amount,
                                       leave_amount=amount,
                                       category=category_obj,
                                       desc=desc,
                                       )
            log_create(None, responsible, cash, action_type='Cash_CREATE_1')

            if to_user_obj:
                cashier_balance_update(to_user_obj.id)

            if User.objects.get(id=from_user).type == '2':
                check_paid_orders(from_user)


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



            to_cashier = CashierUser.objects.filter(user_id=to_user).first()
            if to_cashier:
                CashierUser.objects.filter(user_id=to_user).update(
                    balance=F("balance") + int(amount),
                    updated_at=datetime.datetime.now()
                )

            from_cashier = CashierUser.objects.filter(user_id=from_user).first()
            if from_cashier:
                CashierUser.objects.filter(user_id=from_user).update(
                    balance=F("balance") - int(amount),
                    updated_at=datetime.datetime.now()
                )


            cash = Cash.objects.create(type=2,
                                       from_user_id=from_user,
                                       to_user=to_user_obj,
                                       responsible=responsible,
                                       amount=amount,
                                       category=category_obj,
                                       desc=desc,
                                       )
            if User.objects.get(id=from_user).type == '2':
                check_paid_orders(from_user)
            return cash
    except IntegrityError as e:
        handle_exception(e)
        return e
#
# def cash_out_create(responsible, from_user, to_user, amount, category, desc):
#     try:
#         with transaction.atomic():
#             category_obj = None
#             to_user_obj = None
#             if int(category) != 0:
#                 category_obj = CashCategory.objects.get(id=int(category))
#             if int(to_user) != 0:
#                 to_user_obj = User.objects.get(id=to_user)
#
#
#
#
#
#             CashierUser.objects.filter(user_id=to_user).update(balance=F("balance") + int(amount),updated_at=datetime.datetime.now())
#             CashierUser.objects.filter(user_id=from_user).update(balance=F("balance") - int(amount),updated_at=datetime.datetime.now())
#             cash = Cash.objects.create(type=2,
#                                        from_user_id=from_user,
#                                        to_user=to_user_obj,
#                                        responsible=responsible,
#                                        amount=amount,
#                                        category=category_obj,
#                                        desc=desc,
#                                        )
#
#             if User.objects.get(id=from_user).type == '2':
#                 check_paid_orders(from_user)
#             return cash
#     except IntegrityError as e:
#         handle_exception(e)
#         return e


def cashier_balance_update(cashier_id):
    try:
        with transaction.atomic():
            cashier = CashierUser.objects.filter(user_id=cashier_id).first()
            if not cashier:
                return

            old_cashier = CashierUser.objects.get(pk=cashier.pk)

            total_in = Cash.objects.filter(to_user_id=cashier_id).aggregate(
                t=Coalesce(Sum("amount"), 0)
            )["t"]
            total_out = Cash.objects.filter(from_user_id=cashier_id).aggregate(
                t=Coalesce(Sum("amount"), 0)
            )["t"]

            cashier.balance = total_in - total_out
            cashier.save()

            # 🔹 Değişiklik varsa logla
            log_update(
                request=None,
                created_by_user=None,
                old_instance=old_cashier,
                new_instance=cashier,
                fields=["balance"],
                action_type="CashierUser_UPDATE_2",
                path_url=None
            )

    except IntegrityError as e:
        handle_exception(e)
    except Exception as e:
        handle_exception(e)




# def check_paid_orders(driver_id):
#
#     cash_list = Cash.objects.filter(from_user=driver_id, leave_amount__gt=0)
#     un_pay_part_orders = Order.objects.filter(driver_id=driver_id, status=4, payment_status__in=[1, 2])
#
#     total_cash_amount = cash_list.aggregate(t=Coalesce(Sum("leave_amount"), 0))['t']
#     updated_cash =[]
#     for order in un_pay_part_orders:
#         if total_cash_amount < 1:
#             break
#         order_sold_product_price = order.order_products_total_price - order.driver_fee
#         cash_order_relation = \
#         CashOrderRelation.objects.filter(order=order).aggregate(total_amount=Coalesce(Sum("amount"), 0))['total_amount']
#
#         order_leave_amount = order_sold_product_price - cash_order_relation
#         for cash in cash_list:
#             if order_leave_amount <= 0:
#                 break
#             cash_amount = cash.leave_amount
#             if cash_amount <= 0:
#                 continue
#             amount_to_use = min(order_leave_amount, cash_amount)
#             CashOrderRelation.objects.create(order=order, cash=cash, amount=amount_to_use)
#             cash.leave_amount -= amount_to_use
#             total_cash_amount -= amount_to_use
#             cash.save()
#             order_leave_amount -= amount_to_use
#             updated_cash.append(cash.id)
#         if order_leave_amount <= 0:
#             Order.objects.filter(id=order.id).update(payment_status='3')
#         elif order_sold_product_price > order_leave_amount:
#             Order.objects.filter(id=order.id).update(payment_status='2')
#
#     for c in Cash.objects.filter(id__in=set(updated_cash)):
#         cash_update_main_balances(c)



def check_paid_orders(driver_id):
    print('check_paid_orders')
    cash_list = Cash.objects.filter(from_user=driver_id, person_type='1', leave_amount__gt=0)
    un_pay_part_orders = Order.objects.filter(driver_id=driver_id, status=4, total_driver_payment_status__in=[1, 2]).order_by("driver_status_changed_at")

    total_cash_amount = cash_list.aggregate(t=Coalesce(Sum("leave_amount"), 0))['t']
    updated_cash =[]
    for order in un_pay_part_orders:
        if total_cash_amount < 1: # agar leave amount 0 bo'lsa break qiladi
            break

        cash_order_relation = CashOrderRelation.objects.filter(order=order).aggregate(total_amount=Coalesce(Sum("amount"), 0))['total_amount']

        order_leave_amount = order.total_product_price - order.driver_fee - cash_order_relation
        try:
            with transaction.atomic():
                for cash in cash_list:
                    if order_leave_amount == 0: # agar buyurtma uchun to'lanishi kerak qolgan miqdor 0 bo'lsa
                        # buyurtma 0 ammo holati o'zgarmagan bo'lsa chatoqku
                        # Order.objects.filter(id=order.id).update(total_driver_payment_status='3',
                        #                                          total_driver_payment=cash_order_relation - order.driver_fee,
                        #                                          total_driver_payment_paid_at=datetime.datetime.now()
                        #                                          )

                        old_order = Order.objects.filter(id=order.id).first()
                        if not old_order:
                            return  # veya hata işle

                        # 2️⃣ Güncelleme için Python objesi kullan (update yerine save)
                        order_obj = deepcopy(old_order)  # eski veriyi loglamak için kopya
                        order_obj.total_driver_payment_status = '3'
                        order_obj.total_driver_payment = order.total_product_price - order.driver_fee
                        order_obj.total_driver_payment_paid_at = timezone.now()
                        order_obj.save()

                        # 3️⃣ Değişen alanları logla
                        fields_to_log = ['total_driver_payment_status', 'total_driver_payment',
                                         'total_driver_payment_paid_at']
                        log_update(
                            request=None,
                            old_instance=old_order,
                            new_instance=order_obj,
                            fields=fields_to_log,
                            action_type='Order_UPDATE_1'
                        )

                        continue

                    elif order_leave_amount < 0:
                        from services.notify.send_message import send_message
                        send_message(f"Sayt oson express\n to'lov bo'lishtirishda muammo yuzaga keldi order leave miqdor 0 dan pasaygan orderid{order.id}")
                        continue

                    cash_amount = cash.leave_amount
                    if cash_amount <= 0:
                        continue

                    amount_to_use = min(order_leave_amount, cash_amount)
                    CashOrderRelation.objects.create(order=order, cash=cash, amount=amount_to_use)
                    print('create qilindi')
                    cash.leave_amount -= amount_to_use
                    order.total_driver_payment += amount_to_use
                    total_cash_amount -= amount_to_use
                    cash.save()
                    order_leave_amount -= amount_to_use
                    updated_cash.append(cash.id)

                old_order_copy = deepcopy(order)

                if order_leave_amount <= 0:
                    order.total_driver_payment_status = '3'
                    order.total_driver_payment_paid_at = datetime.datetime.now()
                    order.save()
                elif order.total_product_price > order_leave_amount:
                    order.total_driver_payment_status = '2'
                    order.save()
                fields_to_log = ['total_driver_payment_status', 'total_driver_payment_paid_at']
                log_update(
                    request=None,
                    created_by_user=None,
                    old_instance=old_order_copy,
                    new_instance=order,
                    fields=fields_to_log,
                    action_type='Order_UPDATE_1'
                )

        except IntegrityError as e:
            handle_exception(e)
        except Exception as e:
            handle_exception(e)



from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db import transaction




from django.db import transaction
from django.db.models import Sum




def cancel_sold_order(order_id):
    order = Order.objects.filter(id=order_id, total_driver_payment_status__in=[2, 3]).first()
    if order:
        try:
            with transaction.atomic():
                cash_relation = CashOrderRelation.objects.filter(order=order)

                for c in cash_relation:
                    cash = c.cash
                    cash.leave_amount += c.amount
                    cash.save()
                    c.delete()

                order.total_driver_payment = 0
                order.total_driver_payment_status = '1'
                order.total_driver_payment_paid_at = None
                order.save()

                return True
        except IntegrityError as e:
            handle_exception(e)
            return e
    return True




# def check_and_fix_cash_distribution(cash_id):
def update_paid_orders(cash_id):
    """
    Cash kaydının Order dağıtımı ile tutarlı olup olmadığını kontrol eder.
    Eğer fazla ödeme varsa, son relation'lardan başlayarak düzeltir.
    """
    try:
        cash = Cash.objects.get(id=cash_id, from_user__type='2')
    except Cash.DoesNotExist:
        print(f"Cash id={cash_id} bulunamadı.")
        return

    # Cash'a bağlı tüm relation'ları çekiyoruz
    relations = CashOrderRelation.objects.filter(cash=cash).order_by('-created_at')
    total_related_amount = relations.aggregate(t=Sum('amount'))['t'] or 0

    # Cash.amount ile ilişkili toplam tutarı karşılaştırıyoruz
    if total_related_amount <= cash.amount:
        print(f"✅ Cash id={cash_id} zaten dengede. (toplam={total_related_amount}, amount={cash.amount})")
        return

    # Fazla miktar tespit edildi
    excess = total_related_amount - cash.amount
    print(f"⚠️ Cash id={cash_id} fazla ödeme tespit edildi. {excess} so'm geri alınacak.")

    with transaction.atomic():
        remaining_to_reduce = excess

        for rel in relations:
            if remaining_to_reduce <= 0:
                break

            used_amount = rel.amount
            to_remove = min(used_amount, remaining_to_reduce)
            order = rel.order

            # Order miktarını geri alıyoruz
            if order:
                old_order = Order.objects.get(id=order.id)

                order.total_driver_payment = max(order.total_driver_payment - to_remove, 0)

                # Durum güncelleme
                total_should_pay = order.total_product_price - order.driver_fee
                if order.total_driver_payment == 0:
                    order.total_driver_payment_status = '1'  # To‘lanmagan
                    order.total_driver_payment_paid_at = None  # Qisman to‘langan
                elif order.total_driver_payment < total_should_pay:
                    order.total_driver_payment_status = '2'  # Qisman to‘langan
                    order.total_driver_payment_paid_at = None  # Qisman to‘langan
                else:
                    order.total_driver_payment_status = '3'  # To‘liq to‘langan
                    if order.total_driver_payment_paid_at is None:
                        order.total_driver_payment_paid_at = datetime.datetime.now()

                order.save(update_fields=['total_driver_payment', 'total_driver_payment_status', 'total_driver_payment_paid_at'])

                log_update(
                    request=None,
                    created_by_user=None,
                    old_instance=old_order,
                    new_instance=order,
                    fields=['total_driver_payment', 'total_driver_payment_status', 'total_driver_payment_paid_at'],
                    action_type="Order_UPDATE_1"
                )


            # Relation'dan azaltıyoruz
            rel.amount -= to_remove
            remaining_to_reduce -= to_remove

            if rel.amount <= 0:
                rel.delete()
            else:
                rel.save(update_fields=['amount'])

        # Cash leave_amount güncellemesi
        # (fazlalık kadar cash.leave_amount’ı artırabiliriz veya tekrar hesaplayabiliriz)
        total_used = CashOrderRelation.objects.filter(cash=cash).aggregate(t=Sum('amount'))['t'] or 0
        cash.leave_amount = max(cash.amount - total_used, 0)
        cash.save(update_fields=['leave_amount'])

    print(f"♻️ Cash id={cash_id} başarıyla düzeltildi. Yeni leave_amount={cash.leave_amount}")

