
from config.settings.base import DEVELOPER_TG_CHAT_ID, PROJECT_NAME_FOR_EXCEPTION_BOT, EXCEPTION_BOT_TOKEN
import requests
import traceback
import logging

import logging
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)  # logs klasörü yoksa oluştur

LOG_FILE = os.path.join(LOG_DIR, 'notify_error.log')

developer_logger = logging.getLogger('developer_logger')
developer_logger.setLevel(logging.ERROR)

file_handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

if not developer_logger.handlers:
    developer_logger.addHandler(file_handler)

def send_message(message):
    url = f"https://api.telegram.org/bot{EXCEPTION_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": DEVELOPER_TG_CHAT_ID,
        "text": message,
        "parse_mode": 'HTML',
        "disable_web_page_preview": True,
        "disable_notification": False,
    }
    try:
        response = requests.post(url, data=params)
        return True
    except requests.exceptions.RequestException as e:
        error_message = traceback.format_exc()  # Traceback detaylarını al
        developer_logger.error(f"Telegram send notification error (RequestException):\n{error_message}")
        return False
    except Exception as e:
        error_message = traceback.format_exc()
        developer_logger.error(f"Telegram send notification error (All error Hata):\n{error_message}")
        return False
