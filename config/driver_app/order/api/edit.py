from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from order.models import Order, DefectiveOrderDriverFee, OrderProduct, OrderComment
from config.driver_app.permission import is_driver
from django.db.models import F, Sum
from django.db import transaction, IntegrityError
import json
import datetime
from django.http import JsonResponse
from order.models import DefectiveOrderDriverFee
from order.services.order_warehouse_operation import InsufficientStockError
from services.handle_exception import handle_exception
from services.order.history import save_order_status_history


def update_order_status(order, new_status):
    order.status = new_status
    order.is_site_change = False
    order.updated_at = datetime.datetime.now()
    order.save()


@is_driver
def driver_app_order_api_edit(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                body = json.loads(request.body.decode('utf-8'))
                barcode = None
                order_id = None

                if body.get("barcode", None):
                    if len(body['barcode']) < 13:
                        return JsonResponse({
                            'status': 404,
                            'message': f"Hato skannerlangan type {type(body['barcode'])}, val {body}",
                        })
                    barcode = body['barcode']
                    order = Order.objects.filter(status__in=[3, 4, 5], barcode=barcode, transcation_lock=False, driver_id=request.user.id)

                elif body.get("order_id", None):
                    order_id = body['order_id']
                    order = Order.objects.filter(status__in=[3, 4, 5], id=order_id, transcation_lock=False, driver_id=request.user.id)
                else:
                    order = None

                if order:
                    order = order.first()
                    order_status = int(order.status)

                    if body['next_status'] == 3:
                        if order_status in [4, 6, 5]:
                            order.status = 3
                            order.driver_status = '1'
                            order.driver_status_changed_at=datetime.datetime.now()
                            order.save()
                            save_order_status_history(order, order.status, "Buyurtma haydovchi tarafidan yetkazilmoqdaga olindi",
                                                      request.user,
                                                      'config.driver_app.order.api.edit')
                            return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

                    if body['next_status'] == 4:
                        if order_status in [3, 6, 5]:
                            order.status = 4
                            order.driver_status = '2'
                            order.driver_status_changed_at=datetime.datetime.now()
                            order.save()
                            save_order_status_history(order, order.status, "Buyurtma haydovchi tarafidan sotildiga olindi",
                                                      request.user,
                                                      'config.driver_app.order.api.edit')
                            return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

                    if body['next_status'] == 5:
                        if order_status in [3, 4]:
                            order.status = 5
                            order.driver_status = '3'
                            order.driver_status_changed_at=datetime.datetime.now()
                            OrderComment.objects.create(order=order, user=request.user, message=body['desc'])
                            order.save()
                            save_order_status_history(order, order.status, "Buyurtma haydovchi tarafidan bekor qilindi",
                                                      request.user,
                                                      'config.driver_app.order.api.edit')
                            return JsonResponse({'status': 200, 'messages': "O'zgartirildi"})

                    return JsonResponse({'status': 404, 'messages': "Buyurtma o'zgartirilmadi status to'g'ri kelmagani uchun"})
                return JsonResponse({'status': 404, 'messages': "Bu buyurtma topilmadi"})

        except IntegrityError as e:
            handle_exception(e)
            return JsonResponse({'status': 404, 'messages': f"Saqlashda xatolik mavjud {e}"})

    return JsonResponse({'status': 404, 'messages': "faqat post qabol qilinadi"})


def get_day(day):
    from datetime import timedelta
    result = datetime.datetime.now() + timedelta(days=int(day))
    return result


