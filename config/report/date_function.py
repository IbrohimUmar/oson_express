from calendar import monthrange
import datetime

def get_last_day_of_month(year, month):
    _, last_day = monthrange(year, month)
    return datetime.date(year, month, last_day)