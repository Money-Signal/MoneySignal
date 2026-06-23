"""금융상품 관련 View"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from products.models import FinancialProduct, UserProduct
from products.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    UserProductSerializer,
)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list(request):
    """
    상품 목록 조회
    Query Params:
      - type: 'D'(예금) | 'S'(적금) → 없으면 전체
      - bank: 은행명 (kor_co_nm 포함 검색)
    """
    queryset = FinancialProduct.objects.prefetch_related('options', 'liked_users').all()

    product_type = request.query_params.get('type')
    if product_type in ('D', 'S'):
        queryset = queryset.filter(product_type=product_type)

    bank = request.query_params.get('bank')
    if bank:
        queryset = queryset.filter(kor_co_nm__icontains=bank)

    serializer = ProductListSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_detail(request, product_id):
    """상품 상세 조회 (금리 옵션 포함)"""
    product = get_object_or_404(
        FinancialProduct.objects.prefetch_related('options', 'liked_users'),
        pk=product_id
    )
    serializer = ProductDetailSerializer(product, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_like(request, product_id):
    """
    찜하기 토글
    - 이미 찜한 상품이면 찜 취소
    - 찜하지 않은 상품이면 찜 추가
    """
    product = get_object_or_404(FinancialProduct, pk=product_id)
    user_product = UserProduct.objects.filter(user=request.user, product=product)

    if user_product.exists():
        user_product.delete()
        return Response({'liked': False, 'message': '찜이 취소되었습니다.'}, status=status.HTTP_200_OK)

    UserProduct.objects.create(user=request.user, product=product)
    return Response({'liked': True, 'message': '찜이 완료되었습니다.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liked_product_list(request):
    """현재 로그인 유저의 찜한 상품 목록 조회 (최근 찜한 순)"""
    user_products = (
        UserProduct.objects
        .filter(user=request.user)
        .select_related('product')
        .prefetch_related('product__options', 'product__liked_users')
        .order_by('-created_at')
    )
    serializer = UserProductSerializer(user_products, many=True, context={'request': request})
    return Response(serializer.data)
