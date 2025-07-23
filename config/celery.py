#  type: ignore


REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6375
REDIS_DB = 0

BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# For local redis server
# BROKER_URL = f"redis://{LOCAL_REDIS_HOST}:{LOCAL_REDIS_PORT}/{LOCAL_REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = 'Asia/Tashkent'

# CELERY_BEAT_SCHEDULE = {
#     "sample_task": {
#         "task": "tg.tasks.parser",
#         "schedule": crontab(minute="*/1"),
#     },
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
            "expiry_seconds": 60,
            # "hosts": [("127.0.0.1", 6379)],
        },
    },
}

CELERY_IMPORTS = [
    'config.tasks',
]

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config", broker=CELERY_BROKER_URL)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
