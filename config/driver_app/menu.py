from django.shortcuts import render
from .permission import is_driver

@is_driver
def driver_app_menu(request):
    return render(request, 'driver_app/menu.html', {"o": request.user})
