from django.shortcuts import render
from config.driver_app.permission import is_driver


@is_driver
def driver_app_profile(request):
    return render(request, 'driver_app/profile.html', {"user": request.user})
