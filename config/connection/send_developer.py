




import requests
def send_private_message_developer(messages):
    messages = "Elituvchi : "+str(messages)
    url = "https://api.telegram.org/bot5987201267:AAHUho2camKMj25dgdrGBC6-V3FPRl8Iby4/sendMessage?chat_id={}&text={}".format(
        6937180, messages)
    requests.get(url)
    return True


