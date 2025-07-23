from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from report.models import DriverReport
from user.models import User
from config.connection.send_developer import send_private_message_developer
from config.settings.base import SITE_NAME

@transaction.atomic()
def driver_balance_saver():
    drivers = User.objects.filter(type=2, is_active=True)
    try:
        with transaction.atomic():
            for driver in drivers:
                report = driver.driver_data
                order_status_by = report.order_status_by
                order_product_by = report.order_product_by
                DriverReport.objects.create(
                    driver=driver,
                    debt=report.debt,
                    total_fee=report.fee,

                    total_pay=report.total_payment,
                    balance=report.balance,

                    order_send_product_count=order_status_by['send_products'],
                    order_being_delivered_count=order_status_by['being_delivered'],

                    order_delivered_count=order_status_by['delivered'],
                    order_call_back_count=order_status_by['call_back'],

                    order_cancelled_driver_count=order_status_by['canceled_driver'],
                    order_cancelled_returned_count=order_status_by['canceled_returned'],
                    order_cancelled_given_other_order_count=order_status_by['canceled_given_other_order'],

                    order_send_product_selling_price=order_product_by['send_product'],
                    order_being_delivered_selling_price=order_product_by['being_delivered'],
                    order_delivered_selling_price=report.debt,
                    order_call_back_selling_price=order_product_by['call_back'],
                    order_cancelled_driver_selling_price=order_product_by['cancelled_driver'],
                    order_driver_hand_product_price=order_product_by['total']
                )
            return JsonResponse({"status": 200, 'message': "Olindi"})
    except IntegrityError as e:
        print(e)
        send_private_message_developer(F"{SITE_NAME} haydovchi balansini saqlashda muammo chiqdi muammo : {e}")
        return JsonResponse({"status": 500, "messages": f"Xatolik : {e}"}, status=500)
