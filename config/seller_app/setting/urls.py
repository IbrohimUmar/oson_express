from django.urls import path, include

urlpatterns = [
    path('operator-comment/', include('config.seller_app.setting.operator_comment.urls'))
]