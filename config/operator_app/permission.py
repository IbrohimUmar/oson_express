import datetime
import pytz
from django.core.cache import cache
from django.shortcuts import render
from functools import wraps

WORK_START_HOUR = 7
WORK_START_MINUTE = '00'
WORK_END_HOUR = 23

uzbekistan_timezone = pytz.timezone('Asia/Tashkent')

def is_work_time():
    is_work_time = cache.get('is_work_time')
    if is_work_time is None:
        current_time = datetime.datetime.now(uzbekistan_timezone)
        current_hour = current_time.hour
        is_work_time = 7 <= current_hour < 23
        cache.set('is_work_time', is_work_time, timeout=600)  # Önbelleği 10 dakika boyunca sakla
    return is_work_time



def check_work_hours(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_work_time() and request.user.is_superuser is False:
            return render(request, 'operator_app/permission/not_work_hours.html', {"WORK_START_HOUR":WORK_START_HOUR,
                                                                                   'WORK_START_MINUTE':WORK_START_MINUTE,
                                                                                   'WORK_END_HOUR':WORK_END_HOUR})
        return view_func(request, *args, **kwargs)
    return wrapper

