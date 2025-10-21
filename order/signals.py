from django.db.models.signals import post_save, post_init
from order.models import Order, OrderProduct
from django.dispatch import receiver



# @receiver(post_save, sender=Order)
# def create_profile(sender, instance, created, **kwargs):
#
#     if created:
#         print("create bo'ldi")
#     #     Profile.objects.create(user=instance)
#

from django.db import transaction, IntegrityError
from django.db.models import F, Q

@receiver(post_save, sender=Order)
def save_profile(sender, instance, **kwargs):
        # print('keldi')
        pass
        # if instance.defective_product_order is not None:
        #     if int(instance.status) == "4":
        #         try:
        #             with transaction.atomic():
        #                 OrderProduct.objects.filter(order_id=instance.id).update(status=6, price=F('input_price'))
        #                 sold_order = Order.objects.get(id=instance.defective_product_order)
        #                 sold_order.driver_fee += instance.driver_fee
        #                 sold_order.save()
        #                 instance.status='5'
        #                 instance.save()
        #         except IntegrityError:
        #             print("saqlashda muammo bo'ldi")
        #             instance.status = '5'
        #             instance.save()