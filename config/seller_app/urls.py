from django.urls import path, include
from .home import seller_app_home

urlpatterns = [
    path('home/', seller_app_home, name="seller_app_home"),
    path('marketer/', include('config.seller_app.marketer.urls')),
    path('postage/', include('config.seller_app.postage.urls')),
    path('operator/', include('config.seller_app.operator.urls')),
    path('supplier/', include('config.seller_app.supplier.urls')),
    path('warehouse/', include('config.seller_app.warehouse.urls')),
    path('product/', include('config.seller_app.product.urls')),
    path('cash/', include('config.seller_app.cash.urls')),
    path('orders/', include('config.seller_app.orders.urls')),
    path('setting/', include('config.seller_app.setting.urls')),
    path('report/', include('config.seller_app.report.urls')),

]