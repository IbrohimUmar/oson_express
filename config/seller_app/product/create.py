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

from config.setting.process_image import process_image
from services.handle_exception import handle_exception
from store.services.product_feature import ProductFeatureService
from user.models import User
from store.models import Product, ProductVariable, Colors, Measure, MeasureItem, ProductDeliveryPrice, \
    ProductCollectionItem, ProductApprovalNote

from django import forms

from tinymce.widgets import TinyMCE



class FlatPageForm(forms.ModelForm):
    class Meta:
        model = Product
        widgets = {'desc': TinyMCE(attrs={'cols': 80, 'rows': 30})}
        fields = ['desc']


@login_required(login_url='/login')
@permission_required('admin.seller_app_product_create', login_url="/home")
def seller_app_product_create(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                r = json.loads(request.POST["selected_data_json"])

                image = None
                if request.FILES.get("image", None):
                    image = request.FILES['image']

                uploaded_image = request.FILES.get('image', None)
                high_filename, high_file = process_image(uploaded_image, (1080, 1440), "high")
                small_filename, small_file = process_image(uploaded_image, (180, 240), "small")
                product = Product.objects.create(name=r['name'], short=r['short'],
                                                 desc=request.POST['desc'],
                                                 seller=request.user,
                                                 # image=request.FILES.get('image', None),
                                                 seller_fee={'': 0}.get(r['seller_fee'], r['seller_fee']),
                                                 sale_price={'': 0}.get(r['sale_price'], r['sale_price']),
                                                 is_active={"true": True, "false": False}.get(r['is_active'], r['is_active']),
                                                 toll={"true": True, "false": False}.get(r['toll'], r['toll']),
                                                 is_collection={'1': False, '2': True}.get(r['product_type']))
                product.image.save(high_filename, high_file)
                product.small_image.save(small_filename, small_file)

                ProductApprovalNote.objects.create(
                    product=product,
                    user=request.user,
                    note="Seller tomonidan mahsulot qo'shildi"
                )


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
                if r['product_type'] == "2":
                    collection, created = ProductCollectionItem.objects.get_or_create(product=product)
                    if isinstance(r['selected_collection'], str):
                        selected_collection = r['selected_collection'].split(",")
                    else:
                        selected_collection = r['selected_collection']
                    collection.collection.set(selected_collection)

                messages.success(request, "Ma'lumotlar saqlandi")
                return redirect("seller_app_product_list")
        except IntegrityError as e:
            print(e)
            messages.error(request, f"Sizda hatolik mavjud {e}")
            return redirect("seller_app_product_list")
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
    return render(request, 'seller_app/product/create.html', {'data_json': data_json, "form": form})

