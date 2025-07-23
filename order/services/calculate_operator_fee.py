from django.db.models import Sum
from config.settings.base import OPERATOR_BONUS_FOR_ADDITIONAL_SOLD


def calculate_operator_fee(order_product_item, operator_standard_fee):
    total_order_product_amount = order_product_item.aggregate(t=Sum("quantity"))['t'] or 0
    if total_order_product_amount > 1:
        operator_standard_fee += (total_order_product_amount - 1) * OPERATOR_BONUS_FOR_ADDITIONAL_SOLD
    return operator_standard_fee
