from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from store.models import Product
from config.settings.base import TOLL_AMOUNT

@login_required(login_url='/login')
@permission_required('admin.seller_app_product_details', login_url="/home")
def seller_app_product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'seller_app/product/details.html', {'product':product})
