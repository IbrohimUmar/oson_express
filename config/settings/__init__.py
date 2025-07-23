from split_settings.tools import include, optional

include(
    'base.py',
    'database.py',
    'jwt.py',
    # 'celery.py',
    optional('local_settings.py'),
    # 'logger.py',
)
