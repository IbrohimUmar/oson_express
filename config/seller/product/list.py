import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from store.models import Product, ProductApprovalNote
from user.models import User
from services.handle_exception import handle_exception

@login_required(login_url='/login')
@permission_required('admin.seller_product_list', login_url="/home")
def seller_product_list(request, seller_id):
    seller = get_object_or_404(User, type='6', id=seller_id)
    product = Product.objects.filter(seller_id=seller_id).order_by("approval_status")
    search = request.GET.get("search", None)
    if search:
        product = product.filter(
            Q(name__icontains=search) | Q(short__icontains=search) | Q(id__contains=search))

    is_collection = request.GET.get("is_collection", "0")
    if is_collection != '0':
        product = product.filter(is_collection={'1': False, '2': True}.get(is_collection))

    if request.method == 'POST':
        try:
            with transaction.atomic():
                product = get_object_or_404(Product, seller_id=seller_id, id=request.POST['product_id'], approval_status='1')
                if request.POST.get("action", None):
                    product.approval_status = '2'
                    product.approval_status_updated_by = request.user
                    product.approval_status_updated_at = datetime.datetime.now()
                    product.save()
                    ProductApprovalNote.objects.create(
                        product=product,
                        user=request.user,
                        note="Admin tomonidan mahsulot tasdiqlandi"
                    )
                else:
                    product.approval_status = '3'
                    product.approval_status_updated_by = request.user
                    product.approval_status_updated_at = datetime.datetime.now()
                    product.save()
                    ProductApprovalNote.objects.create(
                        product=product,
                        user=request.user,
                        note=request.POST['comment']
                    )
                messages.success(request, "O'zgartirildi")
                return redirect('seller_product_list', seller_id)

        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect("seller_product_list", seller_id)

    paginator = Paginator(product, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller/product/list.html', {
                                                        'page_obj': queryset,
                                                        'seller': seller,
                                                         'count': product.count()})

