from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required(login_url='/login')
@permission_required('admin.seller_app_menu', login_url="/home")
def seller_app_menu(request):
    return render(request, 'seller_app/menu.html', {"o": request.user})
