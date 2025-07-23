from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.apps import apps




seller_app_permission = [
    ("Sotuvchi app | Profilim ko'rish", 'seller_app_profile'),
    ("Sotuvchi app | Oqimlar ko'rish", 'seller_app_stream_list'),
    ("Sotuvchi app | Menyu bo'limi", 'seller_app_menu'),
    ("Sotuvchi app | Mahsulotlarni ko'rish", 'seller_app_product'),
    ("Sotuvchi app | To'lovlar ro'yxatini o'qish", 'seller_app_payment_list'),
    ("Sotuvchi app | To'lov yaratish", 'seller_app_payment_create'),
    ("Sotuvchi app | Mahsulotni batafsil ma'lumotlarni ko'rish", 'seller_app_product_details'),
    ("Sotuvchi app | Statistika | Buyurtma bo'yicha", 'seller_app_statistic_order'),
    ("Sotuvchi app | Statistika | Oqim bo'yicha", 'seller_app_statistic_stream'),
]

operator_app_permission = [
    ("Operator app | Profilim", 'operator_app_profile'),
    ("Operator app | Menyu", 'operator_app_menu'),
    ("Operator app | Oylik statistika", 'operator_app_monthly_report'),

    ("Operator app | Buyurtmani qabul qilish", 'operator_app_order_details'),

    ("Operator app | Buyurtmani o'zgartirish", 'operator_app_order_edit'),

    ("Operator app | Kiritigan buyurtmalarim", 'operator_app_order_history'),
    ("Operator app | Mening buyurtmalarim", 'operator_app_my_order'),
    ("Operator app | Buyurtma olish", 'operator_app_take_order'),
]

driver_permission = [
    ("Haydovchi | Ro'yxati", 'driver_list'),
    ("Haydovchi | Statistikali ro'yxat", 'driver_list_statistic'),
    ("Haydovchi | Qo'shish", 'driver_create'),
    ("Haydovchi | O'zgartirish", 'driver_edit'),
    ("Haydovchi | Haqida", 'driver_about'),
    ("Haydovchi | Tasdiqlanmagan to'lovlari", 'driver_temp_payment_list'),
    ("Haydovchi | Sana bo'yicha statistika", 'driver_date_by_statistic'),
    ("Haydovchi | Kunlik hisobot", 'driver_daily_report'),

    ("Haydovchi | Buyurtma tarihi", 'driver_order_history'),

    ("Haydovchi | To'lovlari | Ro'yxati", 'driver_payment_list'),
    ("Haydovchi | To'lovlari | Qo'shish", 'driver_payment_create'),

    ("Haydovchi | Hisobot", 'driver_main_report'),

    ("Haydovchi | Ombor bo'limi", 'driver_warehouse'),
    ("Haydovchi | Ombor bo'limi | Amaliyotlar tarixi", 'driver_warehouse_operation_history'),
    ("Haydovchi | Ombor bo'limi | Amaliyotlar tarixi | Buyurtmalari ro'yxati", 'driver_warehouse_operation_history_details_by_order'),
    ("Haydovchi | Ombor bo'limi | Amaliyotlar tarixi | Mahsulotlari ro'yxati", 'driver_warehouse_operation_history_details_by_product'),

    ("Haydovchi | Ombor bo'limi | Mahsulot qaytarish skanner orqali", 'driver_warehouse_operation_return_product_by_order_create_scanner'),

    ("Haydovchi | Ombor bo'limi | Mahsulot yuborish skanner orqali", 'driver_warehouse_operation_send_product_create_scanner'),

]

operator_permission = [
    ("Operator | Boshqaruv | Ro'yxati", 'operator_list'),
    ("Operator | Boshqaruv | Statistikali ro'yxati", 'operator_statistic_list'),

    ("Operator | Boshqaruv | Sana bo'yicha statistika", 'operator_date_by_statistic'),

    ("Operator | Boshqaruv | Haqida batafsil", 'operator_details'),

    ("Operator | Boshqaruv | O'zgartirish", 'operator_edit'),

    ("Operator | Boshqaruv | Qo'shish", 'operator_create'),

    ("Operator | To'lov | Ro'yxati", 'operator_payment_list'),

    ("Operator | To'lov | Qo'shish", 'operator_payment_create'),
]

order_permission = [

    ("Buyurtma | Haqida ", 'order_details'),
    ("Buyurtma | O'zgartirish ", 'order_edit'),
    ("Buyurtma | Chop etish ", 'order_print'),

    ("Buyurtma | barcha buyurtmalar ro'yxati ", 'orders_list_all'),
    ("Buyurtma | Bekor qilinganlar ro'yxati ", 'orders_list_canceled'),
    ("Buyurtma | Kechikayotgan yetkazilmoqdalar ro'yxati ", 'orders_list_delayed_delivery'),

    ("Buyurtma | Dubl buyurtmalar ro'yxati", 'orders_list_double'),
    ("Buyurtma | Ombordan chiqmayotgan buyurtmalar ro'yxati", 'orders_list_late_warehouse_exit'),

    ("Buyurtma | Sotilgan buyurtmalar ro'yxati", 'orders_list_sold'),
]

report_permission = [
    ("Hisobot | Katta balans", 'report_big_balance'),
    ("Hisobot | Asosiy", 'report'),
]

seller_permission = [
    ("Sotuvchi | Yangi qo'shish", 'seller_create'),
    ("Sotuvchi | O'zgartirish", 'seller_edit'),
    ("Sotuvchi | Ro'yxati", 'seller_list'),

    ("Sotuvchi | To'lov | Ro'yxati", 'seller_payment_list'),
    ("Sotuvchi | To'lov | Haqida", 'seller_payment_details'),
]

setting_permission = [
    ("Sozlamalar | Mahsulotlar | Ro'yxati", 'setting_product_list'),
    ("Sozlamalar | Mahsulotlar | Qo'shish", 'setting_product_create'),
    ("Sozlamalar | Mahsulotlar | O'zgartirish", 'setting_product_edit'),
]

cash_permission = [
    ("Kassa | Kassaga sahifasi", 'cash_list'),

    ("Kassa | O'tkazma qila olsinmi", 'cash_transfer'),
    ("Kassa | Chiqim qila olsinmi", 'cash_out_data_json'),
    ("Kassa | Kirim qila olsinmi", 'cash_in_data_json'),
]

warehouse_permission = [
    ("Ombor | Amaliyot | O'zgartirish", 'warehouse_operation_edit'),

    ("Ombor | Elituvchi | Amaliyot | O'zgartirish", 'warehouse_operation_history_1'),
    ("Ombor | Elituvchi | Amaliyot | Kirim qilish", 'warehouse_operation_input_product_1'),
    ("Ombor | Elituvchi | Amaliyot | O'tkazma qilish", 'warehouse_operation_transit_product_1'),

    ("Ombor | Mahsulot biriktirish ", 'warehouse_product_attachment_history'),
    ("Ombor | Mahsulot biriktirish | chop etish ", 'warehouse_product_attachment_packaging_order_print'),

    ("Ombor | Sotib olinishi kerak nahsulotlar", 'warehouse_purchase_main'),

    ("Ombor | Qoldiq mahsulotlarni ko'rish", 'warehouse_operation_transit_product_1'),
]


def sync_permission():
    all_permissions = seller_app_permission + operator_app_permission + driver_permission + operator_permission + order_permission + report_permission + setting_permission + cash_permission + warehouse_permission
    created_permissions = get_or_create_permissions('admin', 'logentry', all_permissions)
    sync_permission_group()
    print('successfully created permissions')
    return True


def sync_permission_group():
    get_or_create_group('Operator', operator_permission)
    get_or_create_group('Operator app', operator_app_permission)
    get_or_create_group('Sotuvchi Panel', seller_app_permission)
    return True


def get_or_create_group(group_name, permissions):
    group, created = Group.objects.get_or_create(name=group_name)
    permission_codes = [code for _, code in permissions]
    permissions = Permission.objects.filter(codename__in=permission_codes)
    for permission in permissions:
        group.permissions.add(permission)
    return group


def seller_app_permission_group():
    group, created = Group.objects.get_or_create(name='Sotuvchi Panel')
    sync_permission()
    permission_codes = [code for _, code in seller_app_permission]
    permissions = Permission.objects.filter(codename__in=permission_codes)
    for permission in permissions:
        group.permissions.add(permission)
    return group


def operator_permission_group():
    sync_permission()
    group = get_or_create_group('Operator', operator_permission)
    return group

def operator_app_permission_group():
    sync_permission()
    group = get_or_create_group('Operator app', operator_app_permission)
    return group



def get_or_create_permissions(app_label, model, permissions):
    content_type, created = ContentType.objects.get_or_create(app_label=app_label, model=model)
    created_permissions = []
    for name, codename in permissions:
        perm, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={'name': name}
        )
        created_permissions.append((perm, created))

    return created_permissions