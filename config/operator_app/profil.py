from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required(login_url='/login')
@permission_required('admin.operator_app_profile', login_url="/home")
def operator_app_profile(request):
    # slider = Slider.objects.filter(is_active=True).order_by("-id")
    # messages = OperatorMessage.objects.filter(type='text').order_by("-id")
    return render(request, 'operator_app/profile.html', {"o": request.user,
                                                         'slider': [], 'operator_messages': []})
