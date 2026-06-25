from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_videos, name='search_videos'),
    path('detail/<str:video_id>/', views.video_detail, name='video_detail'),
    path('related/<str:video_id>/', views.get_related_videos,name='related_videos'),
]