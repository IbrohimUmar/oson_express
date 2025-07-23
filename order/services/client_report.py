from django.db.models import Count, Q

from order.models import Order


class ClientReportService:
    def get_client_phone_order_history(self, customer_phone):
        client_phone_history = Order.objects.filter(customer_phone=customer_phone).aggregate(
            total=Count("id"),
            total_delivered=Count("id", filter=Q(status=4)),
            total_being_delivered=Count("id", filter=Q(status__in=[3, 6])),
            total_accepted=Count("id", filter=Q(status__in=[1, 2])),
        )
        return client_phone_history