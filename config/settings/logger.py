from django.conf import settings

LOG_LEVELS = ['info', 'debug', 'warning', 'error']

LOGS_ROOT = env.LOGS_DIR

LOGGER_NAMES = ['operator_order', 'django', 'celery', 'confirm_order', 'getting_order']


def check_dirs():
    if not os.path.exists(LOGS_ROOT):
        os.makedirs(LOGS_ROOT)

    for app_name in LOGGER_NAMES:
        app_dir = f'{LOGS_ROOT}/{app_name}'
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)


def _get_logging():
    check_dirs()

    handlers = {}
    for level in LOG_LEVELS:
        for name in LOGGER_NAMES:
            handler_name = f'{name}_{level}_handler'
            handlers.update({
                handler_name: {
                    'class': 'logging.FileHandler',
                    'level': f'{level.upper()}',
                    'filename': f'{LOGS_ROOT}{name}/{level}.log',
                    'formatter': 'default',
                }
            })

    data = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s    %(filename)s - %(lineno)d',

            },
        },
        'loggers': {
            name: {
                'handlers': [
                    f'{name}_{level}_handler' for level in LOG_LEVELS
                ],
                'propagate': True,
            }
            for name in LOGGER_NAMES
        },
        'handlers': handlers
    }

    return data


LOGGING = _get_logging()
