from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from warehouse.models import WareHouse


def warehouse_permission_check(view_name, user, warehouse_id):
    if user.is_superuser or user.has_perm(f'admin.{view_name}_{warehouse_id}'):
        return True
    return False



def warehouse_permission_required(perm_field, redirect_url="warehouse_list"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, warehouse_id, *args, **kwargs):
            warehouse = get_object_or_404(WareHouse, id=warehouse_id)
            if not warehouse.has_permission(request.user, perm_field):
                messages.warning(request, "Kechirasiz ushbu bo'liimga kirish uchun sizda ruxsat yo'q")
                return redirect(redirect_url)  # Yetki yoksa yönlendir

            return view_func(request, warehouse_id, *args, **kwargs)  # Yetki varsa devam et

        return _wrapped_view

    return decorator
