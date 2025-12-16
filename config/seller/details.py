from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404, redirect

from config.permission import seller_app_permission_group
from user.models import User

@permission_required('admin.seller_edit', login_url="/")
def seller_details(request, id):
    seller = get_object_or_404(User, id=id)
    seller_data = seller.seller_data

    return render(request, 'seller/details.html',{
        'seller': seller,
        'seller_data': seller_data
    })
