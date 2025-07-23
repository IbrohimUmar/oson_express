from django.forms import ModelForm
from .models import SellerStream


# class SellerStreamForm(ModelForm):
#     class Meta:
#         model = SellerStream
#         fields = ["name", "product", "seller", 'url']
#
#         def save(self, commit=True):
#             # Eğer kullanıcı bir URL girmediyse otomatik bir URL oluştur
#             instance = super(SellerStreamForm, self).save(commit=False)
#             if not instance.url:
#                 instance.url = generate_unique_stream_url()
#             if commit:
#                 instance.save()
#             return instance