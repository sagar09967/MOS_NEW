from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'purchase', views.TranSumViewSet, basename='purchase')
router.register(r'sale',views.SalesViewSet,basename='sale')

urlpatterns = router.urls