from django.urls import path

from . import views

urlpatterns = [
    # 게시글 목록 조회 / 작성
    path('posts/', views.post_list, name='post-list'),

    # 게시글 상세 조회 / 수정 / 삭제
    path('posts/<int:post_id>/', views.post_detail, name='post-detail'),

    # 좋아요 토글
    path('posts/<int:post_id>/like/', views.post_like, name='post-like'),

    # 댓글 목록 조회 / 작성
    path('posts/<int:post_id>/comments/', views.comment_list, name='comment-list'),

    # 댓글 삭제
    path('comments/<int:comment_id>/', views.comment_delete, name='comment-delete'),
]
