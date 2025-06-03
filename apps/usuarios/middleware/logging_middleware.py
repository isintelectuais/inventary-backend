import logging
import json

action_logger = logging.getLogger('action_logger')

class ActionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and 200 <= response.status_code < 400:
            user = "Anônimo"
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_email = request.user.email
                user_id = request.user.id

            log_data = {
                "user_email": user_email,
                "user_id": user_id,
                "http_method": request.method,
                "path": request.path,
                "status_code": response.status_code,
            }

            action_logger.info(json.dumps((log_data)))

        return response