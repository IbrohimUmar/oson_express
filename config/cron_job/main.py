from django.http import JsonResponse
from django.http import HttpResponseNotFound
from services.database.backup import backup_database
from config.settings.base import CRONJOB_TOKEN
from services.driver.driver_balance_saver import driver_balance_saver

#  url : http://127.0.0.1:8000/cron-job/main/13543572340857234875623847562983475698237456928347562938457/driver_balance_save
def cronjob_main(request, code, type):
    if code == CRONJOB_TOKEN and type == 'db_backup' or type == 'driver_balance_save':
        if type == 'db_backup': # 24 soatda 1 marta
            backup_database()
            return JsonResponse({"status": 200, 'message': "Olindi"})
        if type == 'driver_balance_save': # har 1 soatda
            driver_balance_saver()
            return JsonResponse({"status": 200, 'message': "Topshiriq berildi"})
    return HttpResponseNotFound("Page not found")
