import datetime
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from django.db import transaction, IntegrityError
from order.models import MarketerStream, Order, OrderProduct
from config.settings.base import TOLL_AMOUNT, API_ALLOWED_URLS
from config.barcode import barcode_generate
from services.order.history import save_order_status_history


def return_stream_url(value):
    url_to_list = value.replace("/", " ").split()
    return {"stream_url": url_to_list[3]}


def check_stream_url(value):
    url_to_list = value.replace("/", " ").split()
    if len(url_to_list) == 4:
        sites = API_ALLOWED_URLS.get(url_to_list[1].lower(), None)
        stream = MarketerStream.objects.filter(url=url_to_list[3]).exists()
        if not sites or not stream:
            raise serializers.ValidationError("Oqim url noto'g'ri")
    else:
        raise serializers.ValidationError("Oqim url noto'g'ri")


class OrderStreamUrlSerializers(serializers.Serializer):
    stream = serializers.CharField(max_length=50, allow_null=False, validators=[check_stream_url])
    phone = serializers.CharField(max_length=50, allow_null=False)
    name = serializers.CharField(max_length=100, allow_null=False)



@transaction.atomic
def create_order_products_from_stream(stream, order):
    from store.models import ProductCollectionItem
    if stream.product.is_collection:
        collection = ProductCollectionItem.objects.filter(product=stream.product).first()
        # toll true bo'lsa pullik bo'ladi  true
        # is_free true bo'lsa tekin vo'ladi  false
        order_product = OrderProduct.objects.create(order=order,
                                                    product_type="2",
                                                    product=stream.product,
                                                    quantity=1,
                                                    total_quantity=1,
                                                    unit_price=stream.product.sale_price,
                                                    total_unit_price=stream.product.sale_price,
                                                    total_price=stream.product.sale_price,
                                                    is_delivery_free=False if stream.product.toll is True else True,
                                                    delivery_cost=TOLL_AMOUNT if stream.product.toll is True else 0
                                                    )

        order_product.calculate_total_price()
        if collection:
            for c in collection.collection.all():
                OrderProduct.objects.create(order=order, product_type="3",
                                            main_order_product=order_product,
                                            product=c,
                                            quantity=0,
                                            total_quantity=0,
                                            unit_price=0,
                                            is_delivery_free=True
                                            )
    else:
        order_product = OrderProduct.objects.create(order=order,
                                    product=stream.product,
                                    quantity=1,
                                    total_quantity=1,
                                    unit_price=stream.product.sale_price,
                                    total_unit_price=stream.product.sale_price,
                                    total_price=stream.product.sale_price,
                                    is_delivery_free=False if stream.product.toll is True else True,
                                    delivery_cost=TOLL_AMOUNT if stream.product.toll is True else 0
                                    )
        order_product.calculate_total_price()

@transaction.atomic
def create_order(v, request):
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def check_plus_client_phone(value):
        if int(len(str(value))) == 12:
            return f"+{value}"
        return value

    stream = MarketerStream.objects.filter(url=return_stream_url(v["stream"])["stream_url"]).first()
    today = datetime.datetime.today()
    old_order = Order.objects.filter(
        customer_phone=v['phone'],
        marketer_stream=stream,
        created_at__gte=datetime.datetime.now() - datetime.timedelta(days=2)
    ).first()
    if old_order:
        return old_order.id

    seller = stream.marketer.seller
    if seller is None:
        seller = stream.marketer
    order = Order.objects.create(barcode=barcode_generate(),
                                        marketer_stream=stream,
                                        marketer_fee=stream.product.seller_fee,
                                        marketer=stream.marketer,
                                        seller=seller,
                                        customer_name=v['name'],
                                        customer_phone=v['phone'],
                                        status='9',
                                        ip=get_client_ip(request),
                                        user_agent=request.META['HTTP_USER_AGENT'],
                                        where_come_from="3",
                                      )

    create_order_products_from_stream(stream, order)
    # hatolik yo'l kir abor yo'qligi analiz qilish kerak
    # order.update_product_total_price()
    # order.update_product_total_quantity()
    order.total_product_price = order.order_products_total_price
    order.total_product_quantity = order.order_products_total_ordered_amount
    order.save()
    save_order_status_history(order, order.status, "Api orqali buyurtma keldi", order.seller, 'api.order.views')

    return order.id


# tekshirish kerak agar delivery cost agar burontasida

class OrderStreamsUrl(APIView):
    def post(self, request):
        serializers = OrderStreamUrlSerializers(data=request.data)
        if serializers.is_valid():
            try:
                with transaction.atomic():
                    order_id = create_order(serializers.data, request)
                    return Response({"message": f"Buyurtma qabul qilindi - ID:{order_id}", 'status': 200}, status=200)
            except IntegrityError as e:
                print(e)
                return Response({"message": "Internation server error", 'status': 500}, status=500)
        return Response({"message": serializers.errors, 'status': 404}, status=404)

    def get(self, request):
        serializers = OrderStreamUrlSerializers(data=request.data)
        if serializers.is_valid():
            try:
                with transaction.atomic():
                    order_id = create_order(serializers.data, request)
                    return Response({"message": f"Buyurtma qabul qilindi - ID:{order_id}", 'status': 200}, status=200)
            except IntegrityError as e:
                print(e)
                return Response({"message": "Internation server error", 'status': 500}, status=500)
        return Response({"message": serializers.errors, 'status': 404}, status=404)
