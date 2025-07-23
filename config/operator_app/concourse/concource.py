
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required(login_url='/login')
@permission_required('admin.operator_create_new_order', login_url="/home")
def operator_app_concourse(request):
    return render(request, 'operator_app/profile.html', {"o": request.user})

