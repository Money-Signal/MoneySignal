from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Comment, Like, Post
from .serializers import CommentSerializer, PostDetailSerializer, PostListSerializer, PostWriteSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])  # GET은 비로그인도 허용, POST는 로그인 필요
def post_list(request):
    """게시글 목록 조회 / 게시글 작성"""

    if request.method == 'GET':
        posts = Post.objects.select_related('author').prefetch_related('likes', 'comments')
        # category 쿼리 파라미터가 있으면 해당 카테고리만 필터링
        category = request.GET.get('category')
        if category:
            posts = posts.filter(category=category)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    # POST: 클라이언트가 보낸 title, content로 게시글 생성
    serializer = PostWriteSerializer(data=request.data)
    if serializer.is_valid():
        # author는 클라이언트 입력값이 아니라 현재 로그인된 유저로 직접 지정
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, post_id):
    """게시글 상세 조회 / 수정 / 삭제 (수정·삭제는 작성자 본인만)"""

    # pk에 해당하는 게시글이 없으면 자동으로 404 반환
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'GET':
        Post.objects.filter(pk=post_id).update(view_count=post.view_count + 1)
        post.refresh_from_db()
        serializer = PostDetailSerializer(post, context={'request': request})
        return Response(serializer.data)

    # 수정·삭제 요청 시 작성자 본인인지 먼저 확인
    if post.author != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        # 기존 post 객체에 새 데이터를 덮어씌워 수정
        serializer = PostWriteSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: 게시글 삭제 후 본문 없이 204 반환
    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 로그인 유저만 좋아요 가능
def post_like(request, post_id):
    """좋아요 토글 — 없으면 생성, 이미 있으면 취소"""

    post = get_object_or_404(Post, pk=post_id)

    # get_or_create: DB에 해당 (user, post) 조합이 없으면 생성(created=True), 있으면 조회(created=False)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        # 이미 좋아요를 눌렀던 상태 → 취소
        like.delete()
        return Response({'liked': False, 'like_count': post.like_count})

    # 새로 좋아요 누른 경우
    return Response({'liked': True, 'like_count': post.like_count}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_list(request, post_id):
    """댓글 목록 조회 / 댓글 작성"""

    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'GET':
        # 해당 게시글에 달린 댓글만 조회 (작성일 오름차순 - Comment.Meta.ordering)
        serializer = CommentSerializer(post.comments.select_related('author'), many=True)
        return Response(serializer.data)

    # POST: 댓글 작성
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        # author, post는 클라이언트가 보내지 않고 서버에서 직접 지정
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, comment_id):
    """댓글 삭제 (작성자 본인만)"""

    comment = get_object_or_404(Comment, pk=comment_id)

    # 삭제 요청자가 댓글 작성자인지 확인
    if comment.author != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
