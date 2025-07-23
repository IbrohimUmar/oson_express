# from os import path

from .main import cronjob_main
from django.urls import path, include
urlpatterns = [
    # products
    path('main/<int:code>/<str:type>', cronjob_main, name="cronjob_main"),
]