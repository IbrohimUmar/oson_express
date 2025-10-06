import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from order.models import Order
from services.handle_exception import handle_exception
from services.seller.get_seller import get_seller
from user.models import User
from django.db.models import Q
from django.core.paginator import Paginator

from postage.models import Postage, PostageDetails


@login_required(login_url='/login')
@permission_required('admin.seller_app_postage_details', login_url="/home")
def seller_app_postage_details(request, postage_id):
    seller = get_seller(request.user)
    postage = get_object_or_404(Postage, Q(from_user=seller) | Q(to_user=seller), id=postage_id)
    details = PostageDetails.objects.filter(postage=postage)

    '''
    pocha haqida ma'lumotlar
    
    pasda belgilan pochtalar va kim tasdiqlab kim tasdiqlamagan ekanligi
    '''

    paginator = Paginator(details, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/postage/details.html', {
                                                            'postage': postage,
                                                           'queryset': queryset})

