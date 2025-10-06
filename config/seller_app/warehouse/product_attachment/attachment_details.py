from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render




@login_required(login_url='/login')
@permission_required('admin.seller_app_warehouse_product_attachment_list', login_url="/home")
def seller_app_warehouse_product_attachment_details(request, id):
    return render(request, 'seller_app/warehouse/list.html', {})