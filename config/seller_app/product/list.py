from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from store.models import Product





@login_required(login_url='/login')
@permission_required('admin.seller_app_product_list', login_url="/home")
def seller_app_product_list(request):
    product = Product.objects.filter(seller=request.user).order_by("-id")
    search = request.GET.get("search", None)
    if search:
        product = product.filter(
            Q(name__icontains=search) | Q(short__icontains=search) | Q(id__contains=search))

    is_collection = request.GET.get("is_collection", "0")
    if is_collection != '0':
        product = product.filter(is_collection={'1': False, '2': True}.get(is_collection))

    paginator = Paginator(product, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/product/list.html', {'page_obj': queryset, 'count': product.count()})
