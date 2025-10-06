from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from user.models import User

@login_required(login_url='/login')
def seller_app_home(request):
    return render(request, 'seller_app/home.html')

