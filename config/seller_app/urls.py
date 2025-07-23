from django.urls import path, include
from .profile import seller_app_profile
from .menu import seller_app_menu

urlpatterns = [
    path('profile/', seller_app_profile, name="seller_app_profile"),
    path('product/', include('config.seller_app.product.urls')),
    path('stream/', include('config.seller_app.stream.urls')),
    path('statistic/', include('config.seller_app.statistic.urls')),
    path('payment/', include('config.seller_app.payment.urls')),
    path('menu/', seller_app_menu, name="seller_app_menu"),
]