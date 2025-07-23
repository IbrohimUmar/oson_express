from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
# from warehouse.models import WarehouseProductAttachment



# total wiatlariolish kerak
# total waitlarga mos omborda qancha mahsulot belgilash

@login_required(login_url='/login')
@permission_required('admin.warehouse_product_attachment_create', login_url="/home")
def warehouse_product_attachment_create(request):

    return render(request, 'warehouse/product_attachment/create.html', {})