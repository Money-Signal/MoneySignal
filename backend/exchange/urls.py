from django.urls import path
from . import views

urlpatterns = [
    path('prices/', views.get_asset_prices, name='asset_prices'),
    path('news/', views.get_commodity_news, name='commodity_news'),
]