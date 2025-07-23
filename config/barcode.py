import random

from barcode import EAN13
from order.models import Order

def barcode_generate():
    """
    create a unique barcode
    """
    while True:
        new_code = EAN13(str(random.randint(1000000000000, 9999999999999))).get_fullcode()
        if not Order.objects.filter(barcode=int(new_code)).exists():
            return new_code