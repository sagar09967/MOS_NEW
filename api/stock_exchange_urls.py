from . import views, post_feedback_release_views as pfr_views
from rest_framework.routers import DefaultRouter
from django.urls import path, re_path
from .stock_exchange_views import get_list_of_exchanges,get_symbol_list_by_exchange
urlpatterns = [
    path("stock_exchanges",get_list_of_exchanges),
    path("stock_symbols",get_symbol_list_by_exchange)
]