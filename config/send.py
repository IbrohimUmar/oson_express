import json
import requests
from django.core.cache import cache


def get_token():
    token = cache.get('token')
    if token is None:
        payload = {'email': 'Akbarxon648@gmail.com',
                   'password': 'TCLOnva9POvshgPmidsr2hAQinyMOZMYOnwAyL5w'}
        url = "https://notify.eskiz.uz/api/auth/login/"
        headers = {}
        response = requests.post(url, headers=headers, data=payload)
        st = json.loads(response.text)
        data = st['data']
        token = data['token']
        cache.set('token', token, timeout=6600)
    return token


def send_sms_client(phone, message):
    token = get_token()
    url = "https://notify.eskiz.uz/api/message/sms/send/"
    payload = {'mobile_phone': int(phone),
               'message': str(message),
               'from': '4546',
               'callback_url': "http://airshop.uz"}
    files = []
    # headers = {'Authorization': 'Bearer '+ JwtToken.objects.get(id=1).token}
    headers = {'Authorization': 'Bearer '+ str(token)}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.status_code == 401:
        cache.delete('token')
        token = get_token()
        headers = {'Authorization': 'Bearer ' + str(token)}
        response = requests.post(url, headers=headers, data=payload, files=files)
    print(response.text)


def send_sms_driver(phone, message):
    pass

from user.models import User
def bot_send_messages_new(phone, message):
    user = User.objects.filter(username=phone, tg_user_id__isnull=False).first()
    if user:
        responses = requests.get(f'https://api.telegram.org/bot5011901712:AAE5hhBrayrik-I1Ebb6ijL7rd4EOX9pxVM/sendMessage?chat_id={user.tg_user_id}&text={message}')

