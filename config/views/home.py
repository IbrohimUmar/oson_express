from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from user.models import User


def development(request):
    return JsonResponse({"status":200}, safe=False)


@login_required(login_url='/login')
def home(request):
    if request.user.type == "2":
        messages.success(request, "Xush kelibsiz")
        return redirect("driver_app_profile")
    if request.user.type == "4":
        messages.success(request, "Xush kelibsiz")
        return redirect("marketer_app_profile")
    if request.user.type == "3":
        messages.success(request, "Xush kelibsiz")
        return redirect("operator_app_profile")
    if request.user.type == "6":
        messages.success(request, "Xush kelibsiz")
        return redirect("seller_app_home")

    sync_permission = request.GET.get("sync_permission")
    if sync_permission and request.user.is_superuser:
        from config.permission import sync_permission
        sync_permission()
        messages.success(request, "Sinxronlandi")
        return redirect("home")

    return render(request, 'home/index.html')


@login_required(login_url='/login')
def change_color(request):
    user = User.objects.get(id=request.user.id)
    if user.theme == '1':
        change(user, '2')
    elif user.theme == '2' or user.theme == None:
        change(user, '1')
    return JsonResponse({'status': "true"})


def change(user, type):
    user.theme = type
    user.save()


def my_custom_page_not_found_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '404 page not found'})


def my_custom_error_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '500 server error'})


def my_custom_permission_denied_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '403 peremission denied'})


def my_custom_bad_request_view(request, *args, **argv):
    return render(request, 'main_store/error_page.html', {"error": '400 bad request'})
