# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': env.DATABASE_NAME,  # s237904_elituvchi
#         'USER': env.DATABASE_USER,  # s237904_elituvchi
#         'PASSWORD': env.DATABASE_PASSWORD,  # wHyq?Zdm!uc%
#         'HOST': env.DATABASE_HOST,  # localhost
#         'PORT': env.DATABASE_PORT,
#         'OPTIONS': {
#             'sql_mode': 'traditional',
#             'charset': 'utf8mb4',
#
#         }
#     }
# }


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        'NAME': env.DATABASE_NAME,
        'USER': env.DATABASE_USER,
        'PASSWORD': env.DATABASE_PASSWORD,
        'HOST': env.DATABASE_HOST,
        'PORT': env.DATABASE_PORT,
    }
}