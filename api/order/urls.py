from django.urls import path
from .views import OrderStreamsUrl

urlpatterns = [
    path('create', OrderStreamsUrl.as_view()),
]