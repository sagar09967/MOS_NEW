from django.urls import path
from . import sales

urlpatterns = [
    path('retSaleSum/',sales.RetSaleSum.as_view()),  
]