from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from config.driver_app.permission import is_driver



@is_driver
@async_to_sync
async def driver_app_order_main(request):
        district = request.user.allow_districts.all()
        return render(request, 'driver_app/order/main.html',
                    {'district':district})