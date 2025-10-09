import json
from asgiref.sync import async_to_sync, sync_to_async
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from api.order.views import create_order_products_from_stream
from config.barcode import barcode_generate
from order.models import MarketerStream, MarketerStreamClick
import datetime
from order.models import Order
from services.handle_exception import handle_exception
from services.order.history import save_order_status_history
from services.other.get_clicent_ip import get_client_ip


@async_to_sync
async def stream_order_create(request, url):
    stream = await sync_to_async(MarketerStream.objects.filter)(url=url)
    if not stream:
        messages.error(request, "Bunday oqim mavjud emas")
        return redirect('home')

    stream = stream.first()
    MarketerStreamClick.objects.create(marketer_stream=stream)
    product = stream.product
    if request.method == 'POST':
        try:
            with transaction.atomic():


                r = request.POST
                # Tüm boşlukları kaldır
                phone = request.POST['phone'].replace(' ', '')
                today = datetime.datetime.today()
                old_order = Order.objects.filter(
                    customer_phone=phone,
                    marketer_stream=stream,
                    created_at__gte=datetime.datetime.now() - datetime.timedelta(days=2)
                ).first()

                seller = stream.marketer.seller
                if seller is None:
                    seller = stream.marketer


                if not old_order:
                    order = Order.objects.create(barcode=barcode_generate(),
                                                 marketer_stream=stream,
                                                 marketer_id=stream.marketer_id,
                                                 marketer_fee=stream.product.seller_fee,
                                                 seller_id=seller.id,
                                                 total_logistic_fee=stream.product.seller.special_fee_amount,
                                                 customer_name=r['customer_name'],
                                                 customer_phone=phone,
                                                 status='9',
                                                 ip=get_client_ip(request),
                                                 user_agent=request.META['HTTP_USER_AGENT'],
                                                 where_come_from="1",
                                                 )
                    create_order_products_from_stream(stream, order)
                    order.total_product_price = order.order_products_total_price
                    order.total_product_quantity = order.order_products_total_ordered_amount
                    order.save()
                    order.update_driver_fee()
                    order.update_logistic_fee()
                    order.update_seller_fee()
                    save_order_status_history(order, order.status, "Oqim landing page orqali buyurtma keldi", order.marketer,
                                              'config.stream.order_create')
                    messages.success(request, f"Buyurtmangiz qabul qilindi id:{order.id}")
                else:
                    messages.error(request, f"Buyurtmangiz qabul qilib bo'lingan id:{old_order.id}")
                return redirect('stream_order_confirmed', order.id)
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Xatolik yuz berdi {e}")
            return redirect('stream_order_create', url)
    context = {'product': product}
    return render(request, 'stream/order_create.html', context)
