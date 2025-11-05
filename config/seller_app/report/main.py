from django.contrib.auth.decorators import login_required, permission_required

from services.seller.get_seller import get_seller
from user.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from config.format_money import format_money

@login_required(login_url='/login')
@permission_required('admin.seller_app_report_main', login_url="/home")
def seller_app_report_main(request):
    seller = get_seller(request.user)
    return render(request, 'seller_app/report/main.html', {'seller': seller})
