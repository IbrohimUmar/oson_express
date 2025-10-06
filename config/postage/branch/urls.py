from django.urls import path, include
from .residue import postage_branch_residue

urlpatterns = [
    path('seller/', include('config.postage.branch.seller.urls')),
    path('driver/', include('config.postage.branch.driver.urls')),

    path('<int:logistic_branch_id>/residue/', postage_branch_residue, name='postage_branch_residue'),
    # path('branch/', include('config.postage.branch.urls')),
]