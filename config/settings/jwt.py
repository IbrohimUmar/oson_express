from datetime import timedelta

# Simple Jwt settings
#
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'operators.utils.auth.JWTAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
#     'EXCEPTION_HANDLER': 'config.custom_backend.custom_exception_handler',
#     'PAGE_SIZE': 10,
# }
#
# SWAGGER_SETTINGS = {
#     'USE_SESSION_AUTH': False,
#     'SECURITY_DEFINITIONS': {
#         'Bearer': {
#             'type': 'apiKey',
#             'name': 'Authorization',
#             'in': 'header'
#         }
#     }
# }
#
# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(env.ACCESS_TOKEN_LIFETIME)),
#     "REFRESH_TOKEN_LIFETIME": timedelta(hours=float(env.REFRESH_TOKEN_LIFETIME)),
#
#     "ALGORITHM": "HS256",
#     "SIGNING_KEY": env.SECRET_KEY,
#
#     "AUTH_HEADER_TYPES": ("Bearer",),
#     "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
#     "USER_ID_FIELD": "id",
#     "USER_ID_CLAIM": "user_id"
# }
#
# JWT_AUTH = {
#     'JWT_AUTH_COOKIE': 'JWT',  # the cookie will also be sent on WebSocket connections
# }
