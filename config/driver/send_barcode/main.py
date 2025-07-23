import json

from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import get_object_or_404, render
from user.models import User




@login_required(login_url='/login')
@permission_required('admin.driver_send_barcode_main', login_url="/home")
def driver_send_barcode_main(request):
    drivers = User.objects.filter(type=2, is_active=True).values("id", 'first_name', 'last_name', 'username')
    return render(request, 'driver/send_barcode/main.html',
                  {"drivers": json.dumps(list(drivers))})
