from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path,re_path

router = DefaultRouter(trailing_slash=False)
router.register(r'purchase', views.TranSumViewSet, basename='purchase')
router.register(r'sale', views.SalesViewSet, basename='sale')

urlpatterns = router.urls

urlpatterns.append(
    re_path('holdings', views.get_holdings_for_member)
)

urlpatterns.append(
    re_path('capital', views.member_capital_gain)
)
