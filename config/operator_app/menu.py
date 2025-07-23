from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required(login_url='/login')
@permission_required('admin.operator_app_menu', login_url="/home")
def operator_app_menu(request):
    return render(request, 'operator_app/menu.html', {"o": request.user})
