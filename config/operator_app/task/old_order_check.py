import datetime
from django.http import JsonResponse
from order.models import Order

# url name : operator_app_task_old_order_check
# url :  https://elituvchi.savdo24.com//operator-app/task/old-order-check/As2lck9nvoaiej7dpqdmxn3vbouwoidja2slkj4dpas7od1japs22idjoaejnfax
def operator_app_old_order_check(request, key):
    if key == "As2lck9nvoaiej7dpqdmxn3vbouwoidja2slkj4dpas7od1japs22idjoaejnfax":
        date = datetime.datetime.now() - datetime.timedelta(0, 1500) # 25 minute
        order = Order.objects.filter(status=9, operator__isnull=False, updated_at__lte=date)
        order.update(operator=None, updated_at=datetime.datetime.now())
        return JsonResponse({"status": 200, 'order_count':order.count()})
    return JsonResponse({"status": 404})