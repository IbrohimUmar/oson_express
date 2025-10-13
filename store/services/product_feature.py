import json

from django.core.exceptions import ObjectDoesNotExist
from store.models import ProductCollectionItem, ProductVariable, Product


class ProductFeatureService:
    def __init__(self, product):
        self.product = product

    @property
    def get_features(self):
        return {"colors": self.product_get_color_list, "measure": self.product_get_measure,
                "measure_item": self.product_get_measure_item_list, "product_variable": self.product_get_variable_list}

    @property
    def get_collection_all_item_list(self):
        collection = []
        try:
            collection_queryset = ProductCollectionItem.objects.get(product=self.product).collection.all()
            for c in collection_queryset:
                collection_item_feature = ProductFeatureService(c)
                collection.append(collection_item_feature.get_collection_item_features)
            return collection
        except ObjectDoesNotExist:
            return None

    @property
    def get_collection_item_features(self):
        return {"global_id": self.product.id,
                "name": self.product.name,
                "image": self.product.image.url if self.product.image is not None else '',

                'measure': self.product_get_measure,
                "measure_item": self.product_get_measure_item_list,
                "colors": self.product_get_color_list,
                "product_variable": self.product_get_variable_list,
                "selected_measure_item": {},
                "selected_color": {},
                "selected_product_variable": {}
                }

    @property
    def product_bonus_details(self):
        return {"bonus":self.product.bonus, "bonus_amount":self.product.bonus_amount}

    @property
    def product_get_color_list(self):
        if self.product.colors.exists():
            return [{"id": c.id, "name": c.name, "color": c.color, "on_sale": True} for c in self.product.colors.all()]
        return []

    @property
    def product_get_measure(self):
        if self.product.measure:
            return {"id": self.product.measure.id, "short_name": self.product.measure.short_name}
        return {}

    @property
    def product_get_measure_item_list(self):
        if self.product.measure_item.exists():
            return [{"id": item.id, "name": item.name, "on_sale": True} for item in self.product.measure_item.all()]
        return []

    @property
    def product_get_variable_list(self):
        return list(ProductVariable.objects.filter(product=self.product).values("id", "color__name", "color_id",
                                                                                "measure_item__name", "measure_item_id",
                                                                                "is_active", "is_different_price",
                                                                                "price"))
