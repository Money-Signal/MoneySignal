from django.urls import path
from . import views

app_name = 'map'

urlpatterns = [
    path('favorites/', views.favorite_bank_list, name='favorite_bank_list'),
]