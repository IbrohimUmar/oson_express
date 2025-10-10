from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
import json

from config.setting.process_image import process_image
from services.handle_exception import handle_exception
from store.models import Product, ProductVariable, Colors, Measure, MeasureItem, ProductDeliveryPrice, \
    ProductCollectionItem, ProductApprovalNote

@login_required(login_url='/login')
@permission_required('admin.seller_app_product_edit', login_url="/home")
def seller_app_product_edit(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                r = json.loads(request.POST["selected_data_json"])
                product_variable = json.loads(request.POST["product_variable_list"])
                global_is_active = {"true": True, "false": False, 1: True, 0: False}.get(r['is_active'], r['is_active'])

                # product.approval_status = '1'
                product.name = r['name']
                product.short = r['short']
                product.desc = request.POST['desc']
                product.seller_fee = r['seller_fee']
                product.sale_price = r['sale_price']
                product.is_active = global_is_active

                ProductApprovalNote.objects.create(
                    product=product,
                    user=request.user,
                    note="Seller tomonidan mahsulotga o'zgartirish kiriitldi"
                )
                uploaded_image = request.FILES.get('image', None)
                if uploaded_image:
                    high_filename, high_file = process_image(uploaded_image, (1080, 1440), "high")
                    small_filename, small_file = process_image(uploaded_image, (180, 240), "small")
                    product.image.save(high_filename, high_file)
                    product.small_image.save(small_filename, small_file)
                # delivery_price, created = ProductDeliveryPrice.objects.get_or_create(product=product,
                #                                                                      defaults={'price': 0,
                #                                                                                'long_distance_price': 0})

                for v in product_variable:
                    if global_is_active is False:
                        is_active = global_is_active
                    else:
                        is_active = v['is_active']
                    ProductVariable.objects.filter(id=v['id']).update(price=v['price'], is_active=is_active,
                                                                      is_different_price=v['is_different_price'])


                if product.is_collection:
                    collection, created = ProductCollectionItem.objects.get_or_create(product=product)
                    if isinstance(r['selected_collection'], str):
                        selected_collection = r['selected_collection'].split(",")
                    else:
                        selected_collection = r['selected_collection']
                    collection.collection.set(selected_collection)

                else:
                    measure = {"0": None}.get(r['measure'], r['measure'])
                    if measure and product.measure is None:
                        product.measure_id = measure
                        product.save()

                    if len(r['selected_measure_items']) > 0:
                        if isinstance(r['selected_measure_items'], str):
                            selected_measure_items = r['selected_measure_items'].split(",")
                        else:
                            selected_measure_items = r['selected_measure_items']
                        product.measure_item.set(selected_measure_items)

                    if len(r['selected_colors']) > 0:
                        if isinstance(r['selected_colors'], str):
                            selected_colors = r['selected_colors'].split(",")
                        else:
                            selected_colors = r['selected_colors']
                        product.colors.set(selected_colors)

                    print(r)
                    if r['selected_colors'] and r['selected_measure_items']:
                        for color in r['selected_colors']:
                            for size in r['selected_measure_items']:
                                get_, create = ProductVariable.objects.get_or_create(product=product,
                                                                                     measure_item_id=size,
                                                                                     color_id=color,
                                                                                     defaults={'is_first': False,
                                                                                               'is_active': True})
                    elif r['selected_colors']:
                        for color in r['selected_colors']:
                            get_, create = ProductVariable.objects.get_or_create(product=product, measure_item=None,
                                                                                 color_id=color,
                                                                                 defaults={'is_first': False,
                                                                                           'is_active': True})
                    elif r['selected_measure_items']:
                        for size in r['selected_measure_items'] or []:
                            get_, create = ProductVariable.objects.get_or_create(product=product, measure_item_id=size,
                                                                                 color=None,
                                                                                 defaults={'is_first': False,
                                                                                           'is_active': True})
                    else:
                        get_, create = ProductVariable.objects.get_or_create(product=product, measure_item=None,
                                                                             color=None,
                                                                             defaults={'is_first': False,
                                                                                       'is_active': True})

                product.bonus_type = r['product_bonus_type']
                product.bonus = r['product_bonus']
                product.bonus_amount = r['product_bonus_amount']
                product.save()
                messages.success(request, "Ma'lumotlar saqlandi")
                return redirect("seller_app_product_edit", id)
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect("seller_app_product_list")
    measure = None
    measure_is_block = 1

    data_json = {'product_bonus_type': [{"id": 0, "name": "Chegirma mavjud emas"},
                                        {"id": 1, "name": "2+1 shaklidagi chegirma"},
                                        {"id": 2, "name": "2 chisidan mahsulotdan 30 000 mingdan chegirma"}]}
    product_variable_list = []
    selected_data = {
        "delivery_type": "0",
        "product_bonus_type": product.bonus_type,
        "desc": product.desc,
        "product_bonus": product.bonus or 0,
        "product_bonus_amount": product.bonus_amount or 0,
        "selected_collection": [],
        "selected_collection_block": [],
        "selected_colors": list(product.colors.all().values_list("id", flat=True)),
        "selected_colors_block": list(product.colors.all().values_list("id", flat=True)),
        "selected_colors_data": [],
        "selected_measure_items": list(product.measure_item.all().values_list("id", flat=True)),
        "selected_measure_items_block": list(product.measure_item.all().values_list("id", flat=True)),
        "selected_measure_items_data": [],
        "product_type": {True: "2", False: "1"}.get(product.is_collection),
        "product_is_big": 0,
        "standard_district_fee": 0,
        "long_district_fee": 0,
        "name": product.name,
        "short": product.short,
        "seller_fee": product.seller_fee,
        "sale_price": product.sale_price,
        "is_active": {True: 1, False: 0}.get(product.is_active),
        "toll": {True: 1, False: 0}.get(product.toll),
        "measure": {None: '0'}.get(measure, str(measure)),

    }
    if product.is_collection:
        data_json['product_list'] = list(
            Product.objects.filter(is_collection=False).values("id", "name", 'is_active'))
        collection = ProductCollectionItem.objects.filter(product=product).first()
        if collection:
            selected_collection = list(collection.collection.all().values_list("id", flat=True))
            selected_data['selected_collection'] = selected_collection
            # selected_data['selected_collection_block'] = selected_collection
    else:
        product_variable_list = json.dumps(list(
            ProductVariable.objects.filter(product_id=id).order_by("color").values("id", 'measure_item', 'color',
                                                                                   'price', 'is_first', 'is_active',
                                                                                   'is_different_price')))
        data_json["product_variable_block_list"] = list(
            ProductVariable.objects.filter(product_id=id).values_list("id", flat=True))
        data_json['color_list'] = list(Colors.objects.all().values("id", "name", "color"))
        data_json['measure_list'] = list(Measure.objects.all().values("id", "name"))
        data_json['measure_items_list'] = list(MeasureItem.objects.all().values("id", "measure_id", "name"))

        measure = product.measure
        measure_is_block = 1
        if measure:
            measure = measure.id
            measure_is_block = 0

    return render(request, 'seller_app/product/edit.html',
                  {'data_json': json.dumps(data_json), 'selected_data': selected_data,
                   "measure": {None: '0'}.get(measure, str(measure)),
                   "measure_is_block": measure_is_block,
                   "product": product,
                   "product_variable_list": product_variable_list
                   })
