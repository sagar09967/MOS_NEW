from . import views, post_feedback_release_views as pfr_views
from rest_framework.routers import DefaultRouter
from django.urls import path, re_path
from .stock_exchange_views import get_list_of_indexes,get_symbol_list_by_index
urlpatterns = [
    path("indexes",get_list_of_indexes),
    path("symbols",get_symbol_list_by_index)
]