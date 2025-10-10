from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.apps import apps




seller_app_order_permission = [
    ("Seller app | Buyurtmalar | Barcha buyurtmalar | ro'yxati", 'seller_app_orders_list_all'),
    ("Seller app | Buyurtmalar | Barcha buyurtmalar | sotilganlar", 'seller_app_orders_list_sold'),
]

seller_app_postage_permission = [
    ("Seller app | Pochta | ro'yxati", 'seller_app_postage_history'),
    ("Seller app | Pochta | Pochta yuborish", 'seller_app_postage_input'),
    ("Seller app | Pochta | Pochta qaytarish", 'seller_app_postage_return'),
    ("Seller app | Pochta | Pochta haqida ma'lumot", 'seller_app_postage_details'),
]

seller_app_product_permission = [
    ("Seller app | Mahsulot | ro'yxati", 'seller_app_product_list'),
    ("Seller app | Mahsulot | Qo'shish", 'seller_app_product_create'),
    ("Seller app | Mahsulot | Haqida", 'seller_app_product_details'),
    ("Seller app | Mahsulot | O'zgartirish", 'seller_app_product_edit'),
]

seller_app_cash_permission = [
    ("Seller app | Kassa | Main", 'seller_app_cash_main'),
    ("Seller app | Kassa | Chiqim qilish", 'seller_app_cash_out'),
    ("Seller app | Kassa | Chiqimni o'zgartirish", 'seller_app_cash_out_edit'),
]

seller_app_marketer_permission = [
    ("Seller app | Marketolog | Ro'yxati", 'seller_app_marketer_list'),
    ("Seller app | Marketolog | O'zgartirish", 'seller_app_marketer_edit'),
    ("Seller app | Marketolog | Qo'shish", 'seller_app_marketer_create'),

    ("Seller app | Marketolog | To'lov | Ro'yxati", 'seller_app_marketer_payment_list'),
    ("Seller app | Marketolog | To'lov | Haqida", 'seller_app_marketer_payment_details'),
]

seller_app_supplier_permission = [
    ("Seller app | Ta'minotchi | Ro'yxati", 'seller_app_supplier_list'),
    ("Seller app | Ta'minotchi | O'zgartirish", 'seller_app_supplier_edit'),
    ("Seller app | Ta'minotchi | Qo'shish", 'seller_app_supplier_create'),
]



seller_app_operator_permission = [
    ("Seller app | Operator | Boshqaruv | Ro'yxati", 'seller_app_operator_list'),

    ("Seller app | Operator | Boshqaruv | Statistikali ro'yxati", 'seller_app_operator_statistic_list'),

    ("Seller app | Operator | Boshqaruv | Sana bo'yicha statistika", 'seller_app_operator_date_by_statistic'),

    ("Seller app | Operator | Boshqaruv | Haqida batafsil", 'seller_app_operator_details'),

    ("Seller app | Operator | Boshqaruv | O'zgartirish", 'seller_app_operator_edit'),

    ("Seller app | Operator | Boshqaruv | Qo'shish", 'seller_app_operator_create'),

    ("Seller app | Operator | To'lov | Ro'yxati", 'seller_app_operator_payment_list'),

    ("Seller app | Operator | To'lov | Qo'shish", 'seller_app_operator_payment_create'),
]



seller_app_warehouse_permission = [
    ("Seller app | Ombor | Amaliyot | Ro'yxati", 'seller_app_warehouse_list'),

    ("Seller app | Ombor | Sotib olinishi kerak mahsulotlar", 'seller_app_warehouse_purchase_main'),
    ("Seller app | Ombor | Mahsulot biriktirish ", 'seller_app_warehouse_product_attachment_history'),
]


seller_app_setting_permission = [
    ("Seller app | Sozlamalar | Operator izohlari | Ro'yxati", 'seller_app_setting_operator_comment_list'),
    ("Seller app | Sozlamalar | Operator izohlari | Qo'shish", 'seller_app_setting_operator_comment_create'),
    ("Seller app | Sozlamalar | Operator izohlari | O'zgartirish", 'seller_app_setting_operator_comment_edit'),
]


marketer_app_permission = [
    ("Marketingchi app | Profilim ko'rish", 'marketer_app_profile'),
    ("Marketingchi app | Oqimlar ko'rish", 'marketer_app_stream_list'),
    ("Marketingchi app | Menyu bo'limi", 'marketer_app_menu'),
    ("Marketingchi app | Mahsulotlarni ko'rish", 'marketer_app_product'),
    ("Marketingchi app | To'lovlar ro'yxatini o'qish", 'marketer_app_payment_list'),
    ("Marketingchi app | To'lov yaratish", 'marketer_app_payment_create'),
    ("Marketingchi app | Mahsulotni batafsil ma'lumotlarni ko'rish", 'marketer_app_product_details'),
    ("Marketingchi app | Statistika | Buyurtma bo'yicha", 'marketer_app_statistic_order'),
    ("Marketingchi app | Statistika | Oqim bo'yicha", 'marketer_app_statistic_stream'),
]

operator_app_permission = [
    ("Operator app | Profilim", 'operator_app_profile'),
    ("Operator app | Menyu", 'operator_app_menu'),
    ("Operator app | Oylik statistika", 'operator_app_monthly_report'),

    ("Operator app | Buyurtmani qabul qilish", 'operator_app_order_details'),

    ("Operator app | Buyurtmani o'zgartirish", 'operator_app_order_edit'),
    ("Operator app | Buyurtma qo'shish", 'operator_app_order_create'),

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


# order_permission = [
#
#     ("Buyurtma | Haqida ", 'order_details'),
#     ("Buyurtma | O'zgartirish ", 'order_edit'),
#     ("Buyurtma | Chop etish ", 'order_print'),
#
#     ("Buyurtma | barcha buyurtmalar ro'yxati ", 'orders_list_all'),
#     ("Buyurtma | Bekor qilinganlar ro'yxati ", 'orders_list_canceled'),
#     ("Buyurtma | Kechikayotgan yetkazilmoqdalar ro'yxati ", 'orders_list_delayed_delivery'),
#
#     ("Buyurtma | Dubl buyurtmalar ro'yxati", 'orders_list_double'),
#     ("Buyurtma | Ombordan chiqmayotgan buyurtmalar ro'yxati", 'orders_list_late_warehouse_exit'),
#
#     ("Buyurtma | Sotilgan buyurtmalar ro'yxati", 'orders_list_sold'),
# ]

report_permission = [
    ("Hisobot | Katta balans", 'report_big_balance'),
    ("Hisobot | Asosiy", 'report'),
]

# marketer_permission = [
#     ("Sotuvchi | Yangi qo'shish", 'marketer_create'),
#     ("Sotuvchi | O'zgartirish", 'marketer_edit'),
#     ("Sotuvchi | Ro'yxati", 'marketer_list'),
#
#     ("Sotuvchi | To'lov | Ro'yxati", 'marketer_payment_list'),
#     ("Sotuvchi | To'lov | Haqida", 'marketer_payment_details'),
# ]

# setting_permission = [
#     ("Sozlamalar | Mahsulotlar | Ro'yxati", 'setting_product_list'),
#     ("Sozlamalar | Mahsulotlar | Qo'shish", 'setting_product_create'),
#     ("Sozlamalar | Mahsulotlar | O'zgartirish", 'setting_product_edit'),
# ]

cash_permission = [
    ("Kassa | Kassaga sahifasi", 'cash_list'),

    ("Kassa | O'tkazma qila olsinmi", 'cash_transfer'),
    ("Kassa | Chiqim qila olsinmi", 'cash_out_data_json'),
    ("Kassa | Kirim qila olsinmi", 'cash_in_data_json'),
]



def cash_seller_permission():
    from user.models import CashCategory
    name = [
        "Operatorga to'lov",
        "Marketologga to'lov",
        "Ijara uchun to'lov",
        "Taxi uchun to'lov",
        "Boshqa",
            ]
    for i in name:
        CashCategory.objects.get_or_create(
            name=i,
            for_who='2',
            type='2',
        )

def sync_permission():
    all_permissions = marketer_app_permission + operator_app_permission + driver_permission + report_permission + cash_permission
    # cash_seller_permission()
    all_permissions += seller_app_setting_permission + seller_app_cash_permission + seller_app_warehouse_permission + seller_app_order_permission + seller_app_marketer_permission + seller_app_operator_permission + seller_app_postage_permission + seller_app_supplier_permission + seller_app_product_permission
    created_permissions = get_or_create_permissions('admin', 'logentry', all_permissions)
    sync_permission_group()
    print('successfully created permissions')
    return True


def sync_permission_group():
    # get_or_create_group('Operator', operator_permission)
    get_or_create_group('Operator app', operator_app_permission)
    get_or_create_group('Marketolog Paneli', marketer_app_permission)
    # seller_app_permission_group()
    return True


def get_or_create_group(group_name, permissions):
    group, created = Group.objects.get_or_create(name=group_name)
    permission_codes = [code for _, code in permissions]
    permissions = Permission.objects.filter(codename__in=permission_codes)
    for permission in permissions:
        group.permissions.add(permission)
    return group


def marketer_app_permission_group():
    group, created = Group.objects.get_or_create(name='Marketingchi Panel')
    sync_permission()
    permission_codes = [code for _, code in marketer_app_permission]
    permissions = Permission.objects.filter(codename__in=permission_codes)
    for permission in permissions:
        group.permissions.add(permission)
    return group


def seller_app_operator_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app Operator', seller_app_operator_permission)
    return group

def seller_app_marketer_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app marketer', seller_app_marketer_permission)
    return group

def seller_app_order_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app order', seller_app_order_permission)
    return group

def seller_app_postage_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app postage', seller_app_postage_permission)
    return group

def seller_app_product_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app product', seller_app_product_permission)
    return group


def seller_app_cash_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app cash', seller_app_cash_permission)
    return group

def seller_app_supplier_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app supplier', seller_app_supplier_permission)
    return group

def seller_app_warehouse_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app warehouse', seller_app_warehouse_permission)
    return group

def seller_app_setting_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app setting', seller_app_setting_permission)
    return group


def seller_app_permission_group():
    sync_permission()
    group = get_or_create_group('Seller app', seller_app_setting_permission + seller_app_warehouse_permission + seller_app_supplier_permission + seller_app_cash_permission + seller_app_product_permission + seller_app_postage_permission + seller_app_order_permission + seller_app_marketer_permission + seller_app_operator_permission)
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