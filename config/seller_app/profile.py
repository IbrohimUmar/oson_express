from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required(login_url='/login')
@permission_required('admin.seller_app_profile', login_url="/home")
def seller_app_profile(request):
    return render(request, 'seller_app/profile.html', {"o": request.user})
