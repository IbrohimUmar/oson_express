from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from config.driver_app.permission import is_driver


@login_required(login_url='/driver-login/')
@async_to_sync
@is_driver
async def driver_app_order_list(request):
        district = request.user.allow_districts.all()
        return render(request, 'driver_app/order/list.html',
                    {'district':district})