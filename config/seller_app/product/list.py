from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from store.models import Product
from config.settings.base import TOLL_AMOUNT
from order.models import SellerStream
from django.contrib import messages
import string
import random
def generate_unique_stream_url():
    chars = string.ascii_letters + string.digits  # Hem harf hem de rakam kullanacağız
    url = ''.join(random.choices(chars, k=7))
    # Benzersiz olup olmadığını kontrol et
    while SellerStream.objects.filter(url=url).exists():
        url = ''.join(random.choices(chars, k=7))
    return url

@login_required(login_url='/login')
@permission_required('admin.seller_app_product', login_url="/home")
def seller_app_product_list(request):
    product = Product.objects.filter(is_active=True).order_by("-id")
    if request.GET.get("search", None):
        query = request.GET["search"]
        product = product.filter(name__icontains=query)

    if request.method == 'POST':
        r = request.POST
        SellerStream.objects.create(name=r['name'][:240],
                                    seller=request.user,
                                    product_id=r['product_id'],
                                    url=generate_unique_stream_url()
                                    )
        messages.success(request, "Ma'lumotlar saqlandi")
        return redirect("seller_app_product_list")
    paginator = Paginator(product, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/product/list.html', {'queryset': queryset, 'order': queryset, "TOLL_AMOUNT": TOLL_AMOUNT})
