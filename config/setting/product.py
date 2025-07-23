from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
import json

from store.services.product_feature import ProductFeatureService
from user.models import User
from store.models import Product, ProductVariable, Colors, Measure, MeasureItem, ProductDeliveryPrice, \
    ProductCollectionItem


@login_required(login_url='/login')
def setting_product_details_api(request):
    product_id = request.GET.get("product_id", None)
    if product_id:
        global_product = Product.objects.filter(id=product_id).first()
        if global_product:
            product_feature_services = ProductFeatureService(global_product)
            main_data = {
                "is_collection": global_product.is_collection,
                "bonus_type": global_product.bonus_type,
                "bonus_details": product_feature_services.product_bonus_details,
            }
            if global_product.is_collection is False:
                feature = product_feature_services.get_features
                main_data.update(feature)
            else:
                collection = []
                try:
                    collection_queryset = ProductCollectionItem.objects.get(product=global_product).collection.all()
                    for c in collection_queryset:
                        collection_item_feature = ProductFeatureService(c)
                        collection.append(collection_item_feature.get_collection_item_features)
                    main_data['collection_items'] = collection
                except ObjectDoesNotExist:
                    return JsonResponse({'status': 404,
                                         "message": "Bu mahsulot to'plamlari to'liq kiritilmagan adminga murojat qiling"})
            return JsonResponse({
                'status': 200,
                "message": "topildi",
                'data': main_data,
            })
        else:
            return JsonResponse({
                'status': 404,
                'message': "Mahsulot elituvchi id si hato kiritilgan",
            })
    else:
        return JsonResponse({
            'status': 404,
            'message': "Bunday id li mahsulot batafsil ma'lumoti topilmadi adminga murojat qiling",
        })


@login_required(login_url='/login')
@permission_required('admin.setting_product_list', login_url="/home")
def setting_product_list(request):
    product = Product.objects.all().order_by("-id")
    search = request.GET.get("search", None)
    if search:
        product = product.filter(
            Q(name__icontains=search) | Q(short__icontains=search) | Q(id__contains=search))

    is_collection = request.GET.get("is_collection", "0")
    if is_collection != '0':
        product = product.filter(is_collection={'1': False, '2': True}.get(is_collection))

    paginator = Paginator(product, 50)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'setting/product/list.html', {'page_obj': queryset, 'count': product.count()})


from django import forms

from tinymce.widgets import TinyMCE


class FlatPageForm(forms.ModelForm):
    class Meta:
        model = Product
        widgets = {'desc': TinyMCE(attrs={'cols': 80, 'rows': 30})}
        fields = ['desc']


@login_required(login_url='/login')
@permission_required('admin.setting_product_create', login_url="/home")
def setting_product_create(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                r = json.loads(request.POST["selected_data_json"])

                image = None
                if request.FILES.get("image", None):
                    image = request.FILES['image']

                product = Product.objects.create(name=r['name'], short=r['short'],
                                                 desc=request.POST['desc'],
                                                 image=request.FILES.get('image', None),
                                                 seller_fee={'': 0}.get(r['seller_fee'], r['seller_fee']),
                                                 sale_price={'': 0}.get(r['sale_price'], r['sale_price']),
                                                 is_active={"true": True, "false": False}.get(r['is_active'],
                                                                                              r['is_active']),
                                                 is_collection={'1': False, '2': True}.get(r['product_type']))
                if r['product_type'] == "1":
                    product.bonus_type = r['product_bonus_type']
                    product.bonus = r['product_bonus']
                    product.bonus_amount = r['product_bonus_amount']
                    product.save()

                    measure = {"0": None}.get(r['measure'], r['measure'])
                    if measure:
                        product.measure_id = measure
                        product.save()

                    if len(r['selected_measure_items']) > 0:
                        if isinstance(r['selected_measure_items'], str):
                            selected_measure_items = r['selected_measure_items'].split(",")
                        else:
                            selected_measure_items = r['selected_measure_items']
                        product.measure_item.set(selected_measure_items)
                    #
                    if len(r['selected_colors']) > 0:
                        if isinstance(r['selected_colors'], str):
                            selected_colors = r['selected_colors'].split(",")
                        else:
                            selected_colors = r['selected_colors']
                        product.colors.set(selected_colors)

                    if r['selected_colors'] and r['selected_measure_items']:
                        for color in r['selected_colors']:
                            for size in r['selected_measure_items']:
                                ProductVariable.objects.create(product=product, measure_item_id=size, color_id=color,
                                                               is_first=False, is_active=True)
                    elif r['selected_colors']:
                        for color in r['selected_colors']:
                            ProductVariable.objects.create(product=product, color_id=color,
                                                           is_first=False, is_active=True)
                    elif r['selected_measure_items']:
                        for size in r['selected_measure_items'] or []:
                            ProductVariable.objects.create(product=product, measure_item_id=size,
                                                           is_first=False, is_active=True)

                    else:
                        ProductVariable.objects.create(product=product, measure_item=None, color=None,
                                                       is_first=False, is_active=True)
                if r['delivery_type'] == '1':
                    ProductDeliveryPrice.objects.create(type="1",
                                                        product=product,
                                                        price=r['standard_district_fee'],
                                                        long_distance_price=r['long_district_fee'])
                if r['product_type'] == "2":
                    collection, created = ProductCollectionItem.objects.get_or_create(product=product)
                    if isinstance(r['selected_collection'], str):
                        selected_collection = r['selected_collection'].split(",")
                    else:
                        selected_collection = r['selected_collection']
                    collection.collection.set(selected_collection)

                messages.success(request, "Ma'lumotlar saqlandi")
                return redirect("setting_product_list")
        except IntegrityError as e:
            print(e)
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect("setting_product_list")
    data_json = {
        "product_list": list(Product.objects.filter(is_collection=False, is_active=True).values("id", "name")),
        "color_list": list(Colors.objects.all().values("id", "name", "color")),
        "measure_list": list(Measure.objects.all().values("id", "name")),
        "measure_items_list": list(MeasureItem.objects.all().values("id", "measure_id", "name")),

        "product_bonus_type": [{"id": 0, "name": "Chegirma mavjud emas"},
                               {"id": 1, "name": "2+1 shaklidagi chegirma"},
                               {"id": 2, "name": "2 chisidan mahsulotdan 30 000 mingdan chegirma"},
                               ]
    }
    form = FlatPageForm()
    return render(request, 'setting/product/create.html', {'data_json': data_json, "form": form})


@login_required(login_url='/login')
@permission_required('admin.setting_product_list', login_url="/home")
def setting_product_print(request):
    product_variable = ProductVariable.objects.all().values("id", 'barcode', 'product__name', 'color__name',
                                                            'measure_item__name', 'is_active')
    return render(request, 'setting/product/print.html', {"product_variable": product_variable})


@login_required(login_url='/login')
@permission_required('admin.setting_product_edit', login_url="/home")
def setting_product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                r = json.loads(request.POST["selected_data_json"])
                product_variable = json.loads(request.POST["product_variable_list"])
                global_is_active = {"true": True, "false": False, 1: True, 0: False}.get(r['is_active'], r['is_active'])

                product.name = r['name']
                product.short = r['short']
                product.desc = request.POST['desc']
                product.seller_fee = r['seller_fee']
                product.sale_price = r['sale_price']
                product.is_active = global_is_active

                if request.FILES.get("image", None):
                    product.image = request.FILES['image']

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

                # if r['product_is_big']:
                #     delivery_price.price = r['standard_district_fee']
                #     delivery_price.long_distance_price = r['long_district_fee']
                #     delivery_price.save()
                # else:
                #     delivery_price.delete()

                if r['delivery_type'] == '1':
                    delivery_price, created = ProductDeliveryPrice.objects.update_or_create(product=product,
                                                                                            defaults={
                                                                                                'type': '1',
                                                                                                'price': r[
                                                                                                    'standard_district_fee'],
                                                                                                'long_distance_price':
                                                                                                    r[
                                                                                                        'long_district_fee']})
                else:
                    ProductDeliveryPrice.objects.filter(product=product).delete()

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
                return redirect("setting_product_edit", id)
        except IntegrityError as e:
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect("setting_product_list")
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

    shipping_fee_is_dif = ProductDeliveryPrice.objects.filter(product=product).first()
    if shipping_fee_is_dif:
        selected_data['delivery_type'] = shipping_fee_is_dif.type
        selected_data['product_is_big'] = 1
        selected_data['standard_district_fee'] = shipping_fee_is_dif.price or 0
        selected_data['long_district_fee'] = shipping_fee_is_dif.long_distance_price or 0

        selected_data['price_of_two'] = shipping_fee_is_dif.price_of_two or 0
        selected_data['price_of_three'] = shipping_fee_is_dif.price_of_three or 0
        selected_data['price_of_four'] = shipping_fee_is_dif.price_of_four or 0
        selected_data['price_of_five'] = shipping_fee_is_dif.price_of_five or 0

    return render(request, 'setting/product/edit.html',
                  {'data_json': json.dumps(data_json), 'selected_data': selected_data,
                   "measure": {None: '0'}.get(measure, str(measure)),
                   "measure_is_block": measure_is_block,
                   "product": product,
                   "product_variable_list": product_variable_list
                   })
