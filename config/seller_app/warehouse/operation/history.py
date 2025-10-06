import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from config.seller_app.warehouse.services.warehouse_operation_manager import WarehouseOperationManager
from services.handle_exception import handle_exception
from services.seller.get_seller import get_seller
from warehouse.models import WareHouse, WarehouseOperation, WareHouseStock
from django.core.paginator import Paginator
from config.seller_app.warehouse.permission import warehouse_permission_check, warehouse_permission_required
from django.db import transaction, IntegrityError
from order.services.order_warehouse_operation import OrderWarehouseOperationsService
from user.models import User



@login_required(login_url='/login')
@warehouse_permission_required('operation_history')
def seller_app_warehouse_operation_history(request, warehouse_id):
    seller = get_seller(request.user)
    warehouse = get_object_or_404(WareHouse, id=warehouse_id, responsible=seller)
    operations = WarehouseOperation.objects.filter(Q(from_warehouse_id=warehouse_id)|
                                                  Q(to_warehouse_id=warehouse_id), action__in=[1, 2]).order_by("-id")
    warehouse.perms = warehouse.get_user_permission(request.user)

    if request.method == "POST":
        try:
            with (transaction.atomic()):

                params = request.GET.copy()
                url = request.path + '?' + params.urlencode()
                
                r = request.POST
                user = request.user
                status = r['status']
                cancel_note = r.get('note', None)
                operation_id = r.get('operation_id')

                warehouse_operation = WarehouseOperation.objects.select_for_update().filter(Q(from_warehouse_id=warehouse_id)| Q(to_warehouse_id=warehouse_id),id=operation_id, status='1').first()

                if not warehouse_operation:
                    messages.error(request, "Bunday amaliyot mavjud emas")
                    return redirect('seller_app_warehouse_operation_history', warehouse_id)

                if warehouse_operation.action == '2': #omborga ta'minotchidan kirim tasdiqlandi
                    '''
                    Asosiy qilinadigan ishlar
                    1. warehouse operation=status ni o'zgartirish
                    2. stockham in stock qilib qo'yish kerak
                    '''
                    warehouse_operation.status=status
                    warehouse_operation.status_changed_user=request.user
                    warehouse_operation.status_changed_at=datetime.datetime.now()
                    warehouse_operation.desc=cancel_note
                    warehouse_operation.save()
                    if status == '2':
                        warehouse_operation = WareHouseStock.objects.filter(warehouse_operation=warehouse_operation).select_for_update().update(
                            status='1'
                        )
                    messages.success(request, 'Tasdiqlandi')

                if warehouse_operation.action == '1': # ombordan omborga o'tkazma
                    warehouse_operation.status=status
                    warehouse_operation.status_changed_user=request.user
                    warehouse_operation.status_changed_at=datetime.datetime.now()
                    if status == '3':
                        warehouse_operation.desc=cancel_note
                    warehouse_operation.save()
                    if status == '2':
                         WareHouseStock.objects.filter(warehouse_operation=warehouse_operation).select_for_update().update(
                            status='1'
                            )
                         messages.success(request, 'Tasdiqlandi')
                    elif status == '3':
                        related_stocks = WareHouseStock.objects.filter(warehouse_operation=warehouse_operation)
                        for stock in related_stocks:
                            # Y ombordagi ushbu mahsulotni mavjuddan olib tashlaymiz
                            if stock.status != '0':
                                stock.status = '0'
                                stock.save()

                            # X omboriga yangi in_stock qator qo‘shamiz
                            WareHouseStock.objects.create(
                                action_type='7',
                                source_stock=stock,
                                warehouse=warehouse_operation.from_warehouse,
                                product=stock.product,
                                product_variable=stock.product_variable,
                                quantity=stock.quantity,
                                input_price=stock.input_price,
                                lot_number=stock.lot_number,
                                status='1'  # in_stock
                            )
                        messages.success(request, "Bekor qilindi")
                return redirect('seller_app_warehouse_operation_history', warehouse_id)

        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Sizda hatolik {e}")
            return redirect('seller_app_warehouse_operation_history', warehouse_id)


    if request.GET.get("type", "0") != "0":
        query = request.GET["type"]
        operations = operations.filter(action=query).order_by("to_warehouse_status")

    if request.GET.get("from_date", None) and request.GET.get("to_date", None):
        operations = operations.filter(updated_at__date__range=(request.GET['from_date'], request.GET['to_date']))

    paginator = Paginator(operations, 10)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'seller_app/warehouse/operation/history.html', {"page_obj": queryset, 'warehouse':warehouse,"operation_types":WarehouseOperation.action_type})




@login_required(login_url='/login')
def seller_app_warehouse_operation_history_driver(request, warehouse_id):
    if warehouse_permission_check('warehouse_operation_history',request.user, warehouse_id) is False:
        messages.error(request, "Sizga kirish uchun ruxsat yo'q")
        return redirect('seller_app_home')

    warehouse = get_object_or_404(WareHouse, id=warehouse_id)
    operations = WarehouseOperation.objects.filter(action__in=[3, 4, 5]).order_by("-id")
    if request.method == "POST":
        try:
            with transaction.atomic():
                
                params = request.GET.copy()
                url = request.path + '?' + params.urlencode()
                
                r = request.POST
                user = request.user
                position = r['position']
                status = r['status']
                cancel_note = r.get('note', None)
                operation_id = r.get('operation_id')
                if operation_id is not None:
                    if position == "from":
                        operation = WarehouseOperation.objects.select_for_update().filter(id=operation_id,
                                                                                          from_warehouse_status__in=[1, 2]).first()
                    else:
                        operation = WarehouseOperation.objects.select_for_update().filter(id=operation_id,
                                                                                          to_warehouse_status='1').first()
                else:
                    operation = None
                if not operation:
                    messages.error(request, "Holatini o'zgartirib bo'lindi")
                    return redirect('seller_app_warehouse_operation_history', warehouse_id)
                # # permisson check
                if user.is_superuser is False and user.id != 202:
                    if position == "from" and operation.from_warehouse is not None:
                        if operation.from_warehouse.responsible != user:
                            messages.error(request, "Sizda o'zgartirishga izn yo'q")
                            return redirect('seller_app_warehouse_operation_history_driver', warehouse_id)

                    elif position == "to" and operation.to_warehouse is not None:
                        if operation.to_warehouse.responsible != user:
                            messages.error(request, "Sizda o'zgartirishga izn yo'q")
                            return redirect('seller_app_warehouse_operation_history_driver', warehouse_id)
                    else:
                        messages.error(request, "Sizda o'zgartirishga izn yo'q")
                        return redirect('seller_app_warehouse_operation_history_driver', warehouse_id)

                order_warehouse_operations_service = OrderWarehouseOperationsService()

                operation_manager = WarehouseOperationManager()
                if position == "from":
                    if status == "2":
                        operation_manager.operation_from_warehouse_accept(operation, user)
                    if status == "3":
                        if operation.action == "3": # to warehouse driver bo'lsa
                            order_warehouse_operations_service.driver_send_product_cancel(operation, request.user)
                            operation_manager.operation_from_warehouse_cancel(operation, user, cancel_note)
                        elif operation.action == "4": # driver bekor bo'lgan buyurtmalarga stoklarni qo'shib chiqish kerak
                            #  roll back
                            operation_manager.warehouse_operation_driver_return_product_cancel(operation, user, cancel_note)
                            # itemlarniham roll back qildik endi buyurtmalarniham joyiga qaytarish kerak
                            order_warehouse_operations_service.driver_return_product_cancel(operation, request.user)

                        elif operation.action == "5":
                            order_warehouse_operations_service.driver_send_barcode_cancel(operation)
                            operation_manager.warehouse_operation_driver_return_product_cancel(operation, user, cancel_note)

                        else:
                            operation_manager.operation_from_warehouse_cancel(operation, user, cancel_note)
                    # if status == "2":
                    #     operation_manager.operation_from_warehouse_accept(operation, user)
                    # if status == "3":
                    #     if operation.action == "3": # to warehouse driver bo'lsa
                    #         order_warehouse_operations_service.driver_send_product_cancel(operation)
                    #         operation_manager.operation_from_warehouse_cancel(operation, user, cancel_note)
                    #     elif operation.action == "4": # driver bekor bo'lgan buyurtmalarga stoklarni qo'shib chiqish kerak
                    #         #  roll back
                    #         operation_manager.warehouse_operation_driver_return_product_cancel(operation, user, cancel_note)
                    #         # itemlarniham roll back qildik endi buyurtmalarniham joyiga qaytarish kerak
                    #         order_warehouse_operations_service.driver_return_product_cancel(operation)
                    #     else:
                    #         operation_manager.operation_from_warehouse_cancel(operation, user, cancel_note)
                elif position == "to":
                    if status == "2":
                        if operation.from_warehouse_status != "2":
                            messages.error(request, "Dan ombor tasdiqlamagan chiqimni")
                            return redirect('seller_app_warehouse_operation_history', warehouse_id)

                        if operation.to_warehouse:
                            operation = operation_manager.operation_to_warehouse_accept(operation, user)
                        else:

                            operation_manager.operation_accept_to_driver_warehouse(operation, user)

                            if operation.action in ['3']:
                                order_warehouse_operations_service.driver_send_product_accept(operation, request.user)

                            elif operation.action in ['5']:
                                operation = order_warehouse_operations_service.driver_send_barcode_accept(operation)
                            else:
                                raise IntegrityError
                    # if status == "2":
                    #     if operation.from_warehouse_status != "2":
                    #         messages.error(request, "Dan ombor tasdiqlamagan chiqimni")
                    #         return redirect('warehouse_operation_history', warehouse_id)
                    #     if operation.to_warehouse:
                    #         operation = operation_manager.operation_to_warehouse_accept(operation, user)
                    #     else:
                    #         operation = operation_manager.operation_accept_to_driver_warehouse(operation, user)
                    #         order_warehouse_operations_service.driver_send_product_accept(operation)

                    # cancel
                    if status == "3":
                        operation_manager.operation_to_warehouse_cancel(operation, user, cancel_note)
                        if operation.action == "3":
                            order_warehouse_operations_service.driver_send_product_cancel(operation, request.user)


                params = request.GET.copy()
                url = request.path + '?' + params.urlencode()
                messages.success(request, "O'zgartirildi")
                return redirect(url)

        except IntegrityError as e:
            print(e)
            messages.error(request, f"Sizda hatolik {e}")
            return redirect('warehouse_operation_history', warehouse_id)

    if request.GET.get("driver", "0") != "0":
        driver = request.GET["driver"]
        operations = operations.filter(to_warehouse_responsible_id=driver)
        print(driver)

    if request.GET.get("from_warehouse_status", "0") != "0":
        from_warehouse_status = request.GET["from_warehouse_status"]
        operations = operations.filter(from_warehouse_status=from_warehouse_status)

    if request.GET.get("to_warehouse_status", "0") != "0":
        to_warehouse_status = request.GET["to_warehouse_status"]
        operations = operations.filter(from_warehouse_status=to_warehouse_status)


    paginator = Paginator(operations, 10)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)

    drivers = User.objects.filter(type='2', is_active=True)
    return render(request, 'warehouse/operation/history_driver.html', {"page_obj": queryset, 'drivers':drivers, 'warehouse':warehouse,"operation_types":WarehouseOperation.action_type})





@login_required(login_url='/login')
def seller_app_warehouse_operation_product_list(request, warehouse_operation_id):
    seller = get_seller(request.user)
    warehouse_operation = WarehouseOperation.objects.get(id=warehouse_operation_id, seller=seller)
    return render(request, 'seller_app/warehouse/operation/product_list.html', {"warehouse_operation":warehouse_operation})


