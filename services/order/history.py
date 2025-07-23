
from order.models import OrderStatusHistory, Order, OrderProduct

from django.db import transaction, IntegrityError


from django.forms.models import model_to_dict


@transaction.atomic()
def save_order_status_history(order, status, message, responsible_user, modul_name=None):
    try:
        order_products = OrderProduct.objects.filter(order=order)
        order_data = model_to_dict(order)
        products_data = [model_to_dict(product) for product in order_products]
        json_data = {
            'order': order_data,
            'products': products_data
        }
        history = OrderStatusHistory.objects.create(
            order=order,
            status=status,
            message=message,
            responsible=responsible_user,
            json_data=json_data,
            modul_name=modul_name
        )

        history.save()
        return history

    except IntegrityError as e:
        print("An error occurred:", str(e))
        raise e
