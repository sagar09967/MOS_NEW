from django.urls import path
from . import sales

urlpatterns = [
    path('retSaleSum/',sales.RetSaleSum.as_view()),
    path('setSalesDet/',sales.RetSalesDet.as_view()), 
    path('saleSaveAPI/',sales.SaleSaveAPI.as_view()) 
]