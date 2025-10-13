import json

from django.core.exceptions import ObjectDoesNotExist

from store.models import Product, ProductCollectionItem
from store.services.product_feature import ProductFeatureService

from config.settings.base import TOLL_AMOUNT
class ProductListService:
    def get_product_json_by_site(self, site=1, seller=None):
        # all_products = [{'id':i['id'], 'name':i['name'], 'price':i['sale_price'], 'toll':self.get_toll_amount(i['toll'])} for i in Product.objects.filter(seller=seller, approval_status='2', is_active=True).values("id", 'name', 'sale_price', 'toll')]
        all_products = [{'id':i['id'], 'name':i['name'], 'price':i['sale_price'], 'toll':self.get_toll_amount(i['toll'])} for i in Product.objects.filter(seller=seller, is_active=True).values("id", 'name', 'sale_price', 'toll')]
        return all_products

    def get_toll_amount(self, toll):
        if toll == "false" or toll is False:
            return 0
        elif toll == "true" or toll is True:
            return TOLL_AMOUNT
