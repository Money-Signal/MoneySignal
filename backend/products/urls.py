"""금융상품 URL 설정"""

from django.urls import path
from products import views

urlpatterns = [
    path('', views.product_list, name='product-list'),                    # 상품 목록
    path('<int:product_id>/', views.product_detail, name='product-detail'),  # 상품 상세
    path('<int:product_id>/like/', views.product_like, name='product-like'),  # 찜하기 토글
    path('liked/', views.liked_product_list, name='liked-product-list'),  # 찜 목록
]
