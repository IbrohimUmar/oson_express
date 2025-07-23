import random
import asyncio
from datetime import timedelta, datetime

from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.shortcuts import render, redirect
from user.models import TryLogin


def logout_user(request):
    logout(request)
    return redirect('login')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        try_today = TryLogin.objects.filter(ip_address=get_client_ip(request), created_at__gte=datetime.now() - timedelta(days=1))
        if try_today.count() < 60:
            TryLogin.objects.create(ip_address=get_client_ip(request))
            user = authenticate(request, username=int(username), password=password)
            if user is not None:
                    try_today.delete()
                    login(request, user)
                    if request.user.type == '2':
                        messages.success(request, 'Xush kelibsiz')
                        return redirect('driver_app_profile')
                    if request.user.type == "3":
                        messages.success(request, "Xush kelibsiz")
                        return redirect("operator_app_profile")

                    messages.success(request, 'Xush kelibsiz')
                    return redirect('home')
            else:
                return render(request, 'admin_login/login.html',
                          {"login": request.POST['login'], 'password': request.POST['password'] , 'messages_error':"Login yoki parol not'g'ri"})
        else:
            return render(request, 'admin_login/login.html',
                          {"login": request.POST['login'], 'password': request.POST['password'],
                           'messages_error': "Siz tizimga kira olmaysiz chunki juda ko'p xato kiritdingiz"})
    return render(request, 'admin_login/login.html')

