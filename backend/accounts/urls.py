from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, kakao_callback, logout, profile, signup, validate_signup

urlpatterns = [
    path('validate/',        validate_signup,            name='validate_signup'),
    path('signup/',          signup,                     name='signup'),
    path('login/',          LoginView.as_view(),         name='login'),
    path('logout/',         logout,                     name='logout'),
    path('token/refresh/',  TokenRefreshView.as_view(), name='token_refresh'),
    path('kakao/callback/', kakao_callback,             name='kakao_callback'),
    path('me/',             profile,                    name='profile'),
]
