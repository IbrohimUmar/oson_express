from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render




@login_required(login_url='/login')
@permission_required('admin.warehouse_product_attachment_list', login_url="/home")
def warehouse_product_attachment_details(request, id):
    return render(request, 'warehouse/list.html', {})