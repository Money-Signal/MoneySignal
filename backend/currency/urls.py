from django.urls import path
from . import views

urlpatterns = [
    path('latest/', views.latest_rates, name='latest-rates'),
    path('history/<str:currency_code>/', views.chart_data, name='chart-data'),
]