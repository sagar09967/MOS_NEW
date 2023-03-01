from django.urls import path, include
from . import views, post_feedback_release_views as pfr_views
from rest_framework.routers import DefaultRouter
from django.urls import path, re_path

router = DefaultRouter(trailing_slash=False)
router.register(r'purchase', views.TranSumViewSet, basename='purchase')
router.register(r'sale', views.SalesViewSet, basename='sale')
router.register(r'day_trading', views.DayTradingViewSet, basename='day_trading')
router.register(r'feedback', pfr_views.FeedbackViewSet, basename='feedback')
urlpatterns = router.urls

urlpatterns.append(
    re_path('holdings', views.get_holdings_for_member)
)

urlpatterns.append(
    re_path('capital', views.member_capital_gain)
)

urlpatterns.append(
    re_path('market_rate', views.get_market_rate)
)

urlpatterns.append(
    re_path('holding_report', views.get_holding_report)
)

urlpatterns.append(
    re_path('scriptwise_profit_report', views.get_scriptwise_profit_report)
)

urlpatterns.append(
    re_path('profit_adj_report', views.get_profit_adj_report)
)

urlpatterns.append(
    re_path('transaction_report', views.get_transaction_report)
)
urlpatterns.append(
    re_path('profit_chart', views.get_profit_chart)
)

urlpatterns.append(
    re_path('mos_report', views.get_mos_report)
)
urlpatterns.append(
    re_path('script_review_report', views.script_review_report)
)
urlpatterns.append(
    re_path('day_trading_report', views.day_trading_report)
)
urlpatterns.append(
    re_path('portfolio_returns_report', views.portfolio_returns_report)
)

urlpatterns.append(
    re_path('strategy', views.get_strategy)
)

urlpatterns.append(
    re_path('release_notes', pfr_views.ReleaseNoteList.as_view())
)

urlpatterns.append(
    re_path('posts', pfr_views.PostList.as_view())
)

urlpatterns.append(
    re_path('shift_to_trading', views.shift_to_trading)
)
urlpatterns.append(
    re_path('get_otp', views.get_otp)
)
urlpatterns.append(
    re_path('verify_otp', views.verify_otp)
)
urlpatterns.append(
    re_path('set_password', views.set_password)
)



