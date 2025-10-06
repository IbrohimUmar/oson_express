from django.urls import path, include
from .profile import marketer_app_profile
from .menu import marketer_app_menu

urlpatterns = [
    path('profile/', marketer_app_profile, name="marketer_app_profile"),
    path('product/', include('config.marketer_app.product.urls')),
    path('stream/', include('config.marketer_app.stream.urls')),
    path('statistic/', include('config.marketer_app.statistic.urls')),
    path('payment/', include('config.marketer_app.payment.urls')),
    path('menu/', marketer_app_menu, name="marketer_app_menu"),
]