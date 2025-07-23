from connection.send_developer import send_private_message_developer
import json
import requests
from django.db.models import Q
from order.models import Order

MyToken = "as2213dA2Dwwww21kwo12oasaaaaa123aaaaaaaaaadWALKSAMD.KA2KSMaslkdalsjdlkasdA123LDKMAaskdalskdasdas12dasdd213lasdlkasmldsadasdas"
HEADER = {'Content-type': 'application/json',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
          'Accept': 'application/json', 'MyToken': MyToken}


def check_order():
    def json_data(site, url):
        order = Order.objects.filter(site=site, site_order_id__isnull=False, is_site_change=False)

        # if Order.objects.filter(Q(status=3)|Q(status=4)|Q(status=5), site=site, site_order_id__isnull=False, is_site_change=False).exists():
        data = {
            'being_delivered': list(order.filter(status=3).values_list('site_order_id', flat=True)),
            'delivered': list(order.filter(status=4).values_list('site_order_id', flat=True)),
            'canceled': list(order.filter(status=5).values_list('site_order_id', flat=True)),
        }
        send_private_message_developer('data')

        status = try_to_send(url, data)
        if status == 200:
            order.filter(Q(status=3) | Q(status=4) | Q(status=5)).update(is_site_change=True)

    def try_to_send(url, data):
        for a in range(5):
            response = requests.post(url, data=json.dumps(data), headers=HEADER)
            if int(response.status_code) == 200:
                return 200
        send_private_message_developer('saytga ulanib bumadi')
        return 400
    send_private_message_developer('saytga ulanib bumadi')
    response = json_data(1, "https://mahsulot.com/api/order-change-satus-from-elituvchi/")
    return 200


print(check_order())
