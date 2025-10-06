from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required(login_url='/login')
@permission_required('admin.marketer_app_menu', login_url="/home")
def marketer_app_menu(request):
    return render(request, 'marketer_app/menu.html', {"o": request.user})
