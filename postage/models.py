from django.db import models
from django.db.models import Q, Count

from user.models import User
from order.models import Order

from user.models import Regions, Districts



class LogisticBranch(models.Model):
    branch_type = (
        ("1", "Asosiy ombor(haydovchiga chiqim qilad oladigan)"),
        ("2", "Oddiy fileal")
    )
    type = models.CharField(choices=branch_type, max_length=2, default='1', null=True, blank=True)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Regions, models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(Districts, models.SET_NULL, null=True, blank=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



    def get_user_permission(self, user):
        permission = LogisticBranchPermission.objects.filter(user=user, logistic_branch_id=self.id).first()
        return permission

    def has_permission(self, user, perm_field):
        permission = LogisticBranchPermission.objects.filter(user=user, logistic_branch=self).first()
        return getattr(permission, perm_field, False) if permission else False




class LogisticBranchPermission(models.Model):
    logistic_branch = models.ForeignKey(LogisticBranch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    has_view = models.BooleanField(default=True, verbose_name="has_view")

    seller_input = models.BooleanField(default=False, verbose_name="seller_input")
    seller_history = models.BooleanField(default=True, verbose_name="seller_input")
    seller_return = models.BooleanField(default=False, verbose_name="seller_return")

    driver_out = models.BooleanField(default=False, verbose_name="driver_out")
    driver_return = models.BooleanField(default=False, verbose_name="driver_return")

    transfer = models.BooleanField(default=False, verbose_name="transfer")

    history = models.BooleanField(default=False, verbose_name="history")
    residue = models.BooleanField(default=False, verbose_name="residue")


class Postage(models.Model):
    action_type = (
        ("1", "Seller omborga pochta topshirdi"),
        ("2", "Seller ombordan pochtani qaytarib oldi"),
        ("3", "Haydovchi filealdan pochta oldi"),
        ("4", "Haydovchi filealga pochtani qaytarib berdi"),
        ("5", "Filealdan filealga o'tkazma")
    )
    choice_status = (
        ("1", "Tasdiqlanmagan"),
        ("2", "Tasdiqlandi"),
        ("3", "Bekor qilindi"),
    )
    action = models.CharField(choices=action_type, max_length=50, default=1, null=True, blank=True)

    from_logistic_branch = models.ForeignKey(LogisticBranch, related_name="postage_from_logistic_branch", on_delete=models.SET_NULL, null=True, blank=True)
    from_user = models.ForeignKey(User, related_name="postage_from_user", on_delete=models.SET_NULL, null=True, blank=True)
    from_user_status = models.CharField(choices=choice_status, max_length=50, default=1, null=True, blank=True)
    from_user_status_changed_at = models.DateTimeField(null=True, blank=True)

    to_logistic_branch = models.ForeignKey(LogisticBranch, related_name="postage_to_logistic_branch", on_delete=models.SET_NULL, null=True, blank=True)
    to_user = models.ForeignKey(User, related_name="postage_to_user", on_delete=models.SET_NULL, null=True, blank=True)
    to_user_status = models.CharField(choices=choice_status, max_length=50, default=1, null=True, blank=True)
    to_user_status_changed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def postage_details(self):
        return PostageDetails.objects.filter(postage=self)

    @property
    def postage_details_count(self):
        return PostageDetails.objects.filter(postage=self).count()

    @property
    def postage_details_scanned_from_user_count(self):
        return PostageDetails.objects.filter(postage=self, scan_from_user=True).count()

    @property
    def postage_details_scanned_to_user_count(self):
        return PostageDetails.objects.filter(postage=self, scan_to_user=True).count()


    @property
    def postage_orders(self):
        postage_details_id = list(self.postage_details.values_list("order_id", flat=True))
        return Order.objects.filter(id__in=postage_details_id)





    @property
    def relation_order_is_close(self):
        order = self.postage_orders.filter(status__in=[3, 5]).exists()
        if order:
            return False
        return True


    @property
    def relation_order_sold_percentage(self):
        order_status_dict = self.postage_orders.aggregate(
            delivered=Count('id', filter=Q(driver_status=2)),
            canceled=Count('id', filter=Q(driver_status=3)),
            # total=Count('id', filter=Q(status__in=[4, 5])),
            total=Count('id'),
        )

        total_orders = order_status_dict['total'] or 0
        sold_orders = order_status_dict['delivered'] or 0
        sold_percentage = 0
        if total_orders > 0 and sold_orders > 0:
            sold_percentage = (sold_orders / total_orders) * 100
        return {"sold_percentage": int(sold_percentage), "details": order_status_dict}



class PostageDetails(models.Model):
    postage = models.ForeignKey(Postage, on_delete=models.CASCADE, null=False, blank=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    scan_from_user = models.BooleanField(null=False, blank=False, default=False)
    scan_to_user = models.BooleanField(null=False, blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]