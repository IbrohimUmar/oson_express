from config.settings.base import PROJECT_NAME_FOR_EXCEPTION_BOT
from .send_message import send_message
def notify_transaction_error(message_title, error_text):
    message = (
        f"<b>Sayt : {PROJECT_NAME_FOR_EXCEPTION_BOT}</b>\n\n"
        f"<b>Xato : {message_title}</b>\n"
               f"<pre>{error_text}</pre>")
    send_message(message)