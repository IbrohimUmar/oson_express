from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from store.services.product_feature import ProductFeatureService
from store.models import Product,ProductCollectionItem


@login_required(login_url='/login')
def setting_product_details_api(request):
    product_id = request.GET.get("product_id", None)
    if product_id:
        global_product = Product.objects.filter(id=product_id).first()
        if global_product:
            product_feature_services = ProductFeatureService(global_product)
            main_data = {
                "image": global_product.image.url,
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

