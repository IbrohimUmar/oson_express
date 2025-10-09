from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required(login_url='/login')
@permission_required('admin.marketer_app_menu', login_url="/home")
def marketer_app_target_api(request):
    return render(request, 'marketer_app/target_api.html', {"o": request.user})
