import requests
import json
import logging

developer_logger = logging.getLogger('developer_logger')




MyToken = "as2213dA2Dwwww21kwo12oasaaaaa123aaaaaaaaaadWALKSAMD.KA2KSMaslkdalsjdlkasdA123LDKMAaskdalskdasdas12dasdd213lasdlkasmldsadasdas"
HEADER = {'Content-type': 'application/json',
          "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",

          'Accept': 'application/json', 'MyToken': MyToken}


from config.connection.send_developer import send_private_message_developer

def send_ads_order(stream_url, data):
    def get_site_and_stream(url):
        url_to_list = url.replace("/", " ").split()
        if len(url_to_list) == 4:
            sites = {"mahsulot.com": 1, "airshop.uz": 2}.get(url_to_list[1].lower(), None)
            if sites:
                return {'status':200,"site": sites, 'stream_url': url_to_list[3], 'user': url_to_list[2]}
        return {'status': 400, 'messages': "Oqim url xato kiritilgan"}
    def send(data):
        site_url = {1: "https://mahsulot.com", 2:'https://airshop.uz'}.get(data['site'])
        #site_url = {1: "http://127.0.0.1:8080", 2:'http://127.0.0.1:8081'}.get(data['site'])
        try:
            response = requests.post(site_url+'/api/elituvchi-ads-operator/create-order/',
                                     data=json.dumps(data), headers=HEADER, timeout=30)
            if response.status_code != 200:
                developer_logger.info(str("config.operator.ads_order_send_site response.status_code : {response.status_code}"), exc_info=True)
            return response.json()
        except requests.exceptions.RequestException as err:
            developer_logger.info(str("config.operator.ads_order_send_site : {str(err)}"), exc_info=True)
            return {'status': 404, 'messages': "Saytga ulanib bo'lmadi"}
    stream_data = get_site_and_stream(stream_url)
    if stream_data['status'] == 400:
        return stream_data
    stream_data['order_data']=data
    return send(stream_data)