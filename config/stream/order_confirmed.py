import json
from asgiref.sync import async_to_sync, sync_to_async
from django.shortcuts import render, redirect, get_object_or_404
from order.models import Order, MarketerStream

@async_to_sync
async def stream_order_confirmed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'stream/order_confirmed.html', {
        'order':order
    })
