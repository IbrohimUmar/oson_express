import traceback
import logging
from django.http import JsonResponse
from services.notify.notify_transaction_error import notify_transaction_error

logger = logging.getLogger(__name__)

class GlobalExceptionMiddleware:
    """
    Herhangi bir view veya işlemde oluşan istisnaları yakalar,
    loglar ve geliştiriciye bildirir.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            # Eğer response status 500 ise (örneğin custom error raise edilmişse)
            if response.status_code >= 500:
                message = f"Server Error: {response.status_code}, Path: {request.path}"
                logger.error(message)
                err = traceback.format_exc()
                notify_transaction_error(message, err)
                # handle_exception(response)

            return response
        except Exception as e:
            error_message = str(e)
            traceback_details = traceback.format_exc()
            logger.error(f"Unhandled Exception: {error_message}\nTraceback:\n{traceback_details}")
            notify_transaction_error(error_message, traceback_details)
            # Production'da kullanıcıya sade bir yanıt döndür
            return JsonResponse({"detail": "Internal Server Error"}, status=500)
