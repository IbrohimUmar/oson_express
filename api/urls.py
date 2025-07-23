from django.urls import path, include

urlpatterns = [
    path('order/', include('api.order.urls')),
]