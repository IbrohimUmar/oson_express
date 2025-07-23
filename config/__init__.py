import os
from dotenv import load_dotenv
import inspect
from .celery import app as celery_app


__all__ = ('celery_app',)


class EnvConfig:
    DEBUG: bool = True
    PORT: int
    SECRET_KEY: str

    IS_SERVER: True
    TOLL_AMOUNT: int
    CRONJOB_TOKEN: int

    ACCESS_TOKEN_LIFETIME: int = 10  # minutes
    REFRESH_TOKEN_LIFETIME: float = 24  # hours

    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_PORT: int
    DATABASE_HOST: str

    LOGS_DIR: str = '/var/log/operator_logs/'

    REDIS_PASS: str
    REDIS_USER: str
    REDIS_PORT: int
    REDIS_HOST: str

    API_KEY: str
    USER_NAME: str

    MY_BAZAR_TOKEN: str
    PREMIUMSHOP_TOKEN: str
    MAHSULOT_TOKEN: str
    AIRSHOP_TOKEN: str
    SAVDO24_TOKEN: str

    def __init__(self):
        load_dotenv()
        self.__get_variables()

    @classmethod
    def __get_variables(cls):
        attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        keys = dict(attributes).get('__annotations__').items()
        for k, t in keys:
            var = os.environ.get(k.upper()) or os.environ.get(k.lower(), dict(attributes).get(k))
            if t is not bool:
                setattr(cls, k, var)
            else:
                if var in ['False', 'false', 'FALSE']:
                    setattr(cls, k, False)
                else:
                    setattr(cls, k, bool(var))


env = EnvConfig()
