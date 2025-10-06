import traceback
import logging
from services.notify.notify_transaction_error import notify_transaction_error

logger = logging.getLogger(__name__)

def handle_exception(e, notify_admin=True):
    error_message = str(e)
    traceback_details = traceback.format_exc()
    print(f"Exception occurred: {error_message}\nTraceback:\n{traceback_details}")
    logger.error(f"Exception occurred: {error_message}\nTraceback:\n{traceback_details}")
    if notify_admin:
        # send_private_message_developer(f"{error_message}, \n{traceback_details}")
        notify_transaction_error(error_message, traceback_details)