import requests
# from config.connection.order import OrderSite
from order.models import OrderSite
import json

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
    'MyToken': 'as2213dA2Dwwww21kwo12oasaaaaa123aaaaaaaaaadWALKSAMD.KA2KSMaslkdalsjdlkasdA123LDKMAaskdalskdasdas12dasdd213lasdlkasmldsadasdas'}
api_site_url = {"1": "mahsulot.com/api", "2": "airshop.uz/api", "3": "savdo24.com", "4": "mybazar24.uz"}


# -----------------------get new order list
def get_site_order(site):
    value = requests.get("https://" + api_site_url.get(str(site)) + "/rest-api-orders-site/accepted-order-list",
                         headers=headers).json()
    ready = check_new_orders(site, value)
    return ready

def check_new_orders(site, list):
    new_list = []
    old_list = set(old_order_id_site(site))
    for a in list:
        if a['id'] in old_list:
            print('double')
        else:
            new_list.append(a)
    return new_list


def old_order_id_site(site):
    return [a.order_id for a in OrderSite.objects.filter(site=site)]
# -----------------------------end get ner order list


# ----------------------order details
def check_details_order(site, order_id):
    old_order_id_list = set(old_order_id_site(site))
    if order_id in old_order_id_list:
        return False
    return True

def order_details_sites(site, order_id):
    return requests.get(
        "https://" + api_site_url.get(str(site)) + "/rest-api-orders-site/order-details/" + str(order_id),
        headers=headers).json()

# -----------------------end order details


# --------------------------order change status

def order_change_status(site, order_id, status):
    if site == '1':
        statuses = {"2": 2, "3": 3, "4": 4, "5": 6, "6": 8}  # mahsulot
    else:
        statuses = {"2": 2, "3": 3, "4": 4, "5": 6, "6": 7}  # other site
    payload = {"order_id": order_id, 'status': int(statuses.get(str(status)))}
    url = "https://" + api_site_url.get(str(site)) + "/rest-api-orders-site/order-change-status"
    r = requests.get(url, headers=headers, data=json.dumps(payload))
    return r