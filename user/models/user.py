from django.contrib.auth.models import AbstractUser

from django.db import models
from django.db.models import Q


class Regions(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    def __str__(self):  return str(self.name)


class Districts(models.Model):
    region = models.ForeignKey(Regions, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    def __str__(self):  return str(self.name)




class User(AbstractUser):
    birthday = models.DateField(null=True, blank=True, verbose_name='Tug\'ilgin kuni')
    region = models.ForeignKey(Regions, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Viloyati')
    district = models.ForeignKey(Districts, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Tumani')
    street = models.CharField(max_length=350, null=True, blank=True, verbose_name="Ko'cha")
    my_unique_code = models.BigIntegerField(blank=True, null=True, unique=True, verbose_name='Maxsus kodi')
    tg_user_id = models.BigIntegerField(blank=True, null=True, unique=True, verbose_name='Telegram user idsi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
