from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from order.models import Order, OrderProduct, CashOrderRelation


@login_required(login_url='/login')
@permission_required('admin.order_details', login_url="/home")
def order_details(request, id):
    order = get_object_or_404(Order, id=id)
    order_products = OrderProduct.objects.filter(order=order)
    order_cash_relations = CashOrderRelation.objects.filter(order=order)


    # from django.db.models import Sum
    # total_cash_amount = order_cash_relations.aggregate(t=Sum("amount"))['t']
    # if total_cash_amount != order.total_driver_payment:
    #     order.total_driver_payment = total_cash_amount
    #     order.total_driver_payment_status = '2'
    #     order.total_driver_payment_paid_at = None
    #     order.save()



    return render(request, 'order/details.html', {
        'order':order, 'order_products':order_products, 'order_cash_relations':order_cash_relations
                                                          })
