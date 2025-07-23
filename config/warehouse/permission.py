


def warehouse_permission_check(view_name, user, warehouse_id):
    if user.is_superuser or user.has_perm(f'admin.{view_name}_{warehouse_id}'):
        return True
    return False

