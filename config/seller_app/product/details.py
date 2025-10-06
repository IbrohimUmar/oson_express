from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
import json

from config.setting.process_image import process_image
from services.handle_exception import handle_exception
from store.models import Product, ProductVariable, Colors, Measure, MeasureItem, ProductDeliveryPrice, \
    ProductCollectionItem, ProductApprovalNote



@login_required(login_url='/login')
@permission_required('admin.seller_app_product_details', login_url="/home")
def seller_app_product_details(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user)
    comments = ProductApprovalNote.objects.filter(product=product)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if request.POST.get("comment", None):
                    ProductApprovalNote.objects.create(
                        product=product,
                        user=request.user,
                        note=request.POST['comment']
                    )
                    messages.success(request, "Izoh qo'shildi")
                    return redirect('setting_product_details', id)
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect('setting_product_details', id)
    return render(request, 'seller_app/product/details.html',
                  {
                      'comments': comments,
                      'seller': request.user,
                      'product': product
                  })


