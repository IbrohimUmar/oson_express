import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from services.handle_exception import handle_exception
from django.db import IntegrityError, transaction

from store.models import Product, ProductApprovalNote
from user.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

@login_required(login_url='/login')
@permission_required('admin.seller_product_details', login_url="/home")
def seller_product_details(request, seller_id, product_id):
    seller = get_object_or_404(User, id=seller_id)
    product = get_object_or_404(Product, seller=seller, id=product_id)
    comments = ProductApprovalNote.objects.filter(product=product)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if request.POST.get("action", None) == 'size_type_change':
                    product.size_type = request.POST['size_type']
                    if request.POST['size_type'] == '1':
                        product.size_based_delivery_extra = 0
                    else:
                        product.size_based_delivery_extra = request.POST['diff_delivery_price']
                    product.save()
                    messages.success(request, "Yo'l kira o'zgartirildi")
                    return redirect('seller_product_details', seller_id, product_id)

                if request.POST.get("comment", None) and request.POST.get("action", None) is None:
                    ProductApprovalNote.objects.create(
                        product=product,
                        user=request.user,
                        note=request.POST['comment']
                    )
                    messages.success(request, "Izoh qo'shildi")
                    return redirect('seller_product_details', seller_id, product_id)


                product = get_object_or_404(Product, seller_id=seller_id, id=request.POST['product_id'])
                if request.POST.get("action", None) == 'confirm':
                    product.approval_status = '2'
                    product.approval_status_updated_by = request.user
                    product.approval_status_updated_at = datetime.datetime.now()
                    product.save()
                    ProductApprovalNote.objects.create(
                        product=product,
                        user=request.user,
                        note="Admin tomonidan mahsulot tasdiqlandi"
                    )
                elif request.POST.get("action", None) == 'cancel':
                    product.approval_status = '3'
                    product.approval_status_updated_by = request.user
                    product.approval_status_updated_at = datetime.datetime.now()
                    product.save()
                    ProductApprovalNote.objects.create(
                        product=product,
                        user=request.user,
                        note=f"Bekor qilinishi sababi : {request.POST['comment']}"
                    )
                messages.success(request, "O'zgartirildi")
                return redirect('seller_product_details', seller_id, product_id)

        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect('seller_product_details', seller_id, product_id)
    return render(request, 'seller/product/details.html', {
                                                        'comments': comments,
                                                        'seller': seller,
                                                        'product': product})

