"""금융상품 관련 View"""

import os
from openai import OpenAI
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count

from products.models import FinancialProduct, UserProduct
from products.chroma_client import get_collection
from products.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    UserProductSerializer,
)

# GMS 임베딩 클라이언트 (build_embeddings와 동일한 모델 사용)
gms_client = OpenAI(
    api_key=os.environ.get('GMS_KEY'),
    base_url='https://gms.ssafy.io/gmsapi/api.openai.com/v1',
)
EMBEDDING_MODEL = 'text-embedding-3-small'


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list(request):
    """
    상품 목록 조회
    Query Params:
      - type: 'D'(예금) | 'S'(적금) → 없으면 전체
      - bank: 은행명 (kor_co_nm 포함 검색)
    """
    queryset = (
        FinancialProduct.objects
        .prefetch_related('options', 'liked_users')
        .annotate(like_cnt=Count('liked_users'))
        .order_by('-like_cnt')
    )

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
@permission_classes([IsAuthenticatedOrReadOnly])
def recommend_products(request):
    """
    맞춤 상품 추천 (RAG 기반)

    로그인 + 금융정보 입력 유저:
      1. 유저 프로필 → 자연어 텍스트 변환
      2. GMS API로 텍스트 임베딩
      3. ChromaDB 코사인 유사도 검색 (preferred_product_type 하드 필터)
      4. 결과 product_id로 DB 조회 + investment_period 필터(최대 기간 이하)
      5. 상위 5개 반환

    비로그인 or 금융정보 미입력 유저:
      → 인기상품(최고금리 기준 상위 5개) 반환
    """
    user = request.user

    # 비로그인 → 로그인 유도
    if not user.is_authenticated:
        return Response({'type': 'not_logged_in', 'results': []})

    # 로그인했지만 금융정보 미입력 → 빈 결과 반환 (프론트에서 유도 배너 표시)
    has_profile = any([user.investment_type, user.financial_goal, user.occupation, user.age_group])
    if not has_profile:
        return Response({'type': 'no_profile', 'results': []})

    try:
        # --- STEP 1: 유저 프로필 → 자연어 텍스트 ---
        profile_text = _build_user_profile_text(user)

        # --- STEP 2: 텍스트 임베딩 ---
        response = gms_client.embeddings.create(model=EMBEDDING_MODEL, input=profile_text)
        user_vector = response.data[0].embedding

        # --- STEP 3: ChromaDB 유사도 검색 ---
        # preferred_product_type 기반 하드 필터
        # BOTH(상관없음) 이거나 미설정이면 전체 탐색
        where_filter = None
        ptype = getattr(user, 'preferred_product_type', None)
        if ptype == 'DEPOSIT':
            where_filter = {'product_type': 'D'}
        elif ptype == 'SAVING':
            where_filter = {'product_type': 'S'}

        collection = get_collection()
        query_kwargs = {
            'query_embeddings': [user_vector],
            'n_results': min(20, collection.count()),  # 후속 DB 필터를 위해 여유있게 조회
        }
        if where_filter:
            query_kwargs['where'] = where_filter

        results = collection.query(**query_kwargs)
        candidate_ids = [int(pid) for pid in results['ids'][0]]

        if not candidate_ids:
            return Response({'type': 'personalized', 'results': []})

        # --- STEP 4: DB 조회 + investment_period 필터 ---
        # ChromaDB 유사도 순서를 보존하기 위해 id 순서 기반 정렬
        queryset = FinancialProduct.objects.prefetch_related('options', 'liked_users').filter(
            id__in=candidate_ids
        )

        # investment_period = 최대 투자 기간 → 그 이하인 옵션을 가진 상품만
        investment_period = getattr(user, 'investment_period', None)
        if investment_period:
            queryset = queryset.filter(options__save_trm__lte=investment_period).distinct()

        # ChromaDB가 반환한 유사도 순서대로 정렬 (id 리스트 순서 보존)
        id_order = {pid: idx for idx, pid in enumerate(candidate_ids)}
        products = sorted(queryset, key=lambda p: id_order.get(p.id, 999))[:5]

        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response({
            'type': 'personalized',
            'results': serializer.data,
        })

    except Exception:  # pylint: disable=broad-except
        return Response({'type': 'personalized', 'results': []})


def _build_user_profile_text(user):
    """
    유저 프로필을 임베딩용 자연어 텍스트로 변환.

    상품 텍스트(가입대상, 우대조건)에 등장하는 키워드와
    의미적으로 유사하도록 자연어 형태로 작성.
    예: "직장인" → 상품의 "급여이체 우대", "직장인 전용" 텍스트와 매칭
    """
    INVESTMENT_TYPE_MAP = {
        'CONSERVATIVE': '안정형 - 원금 보호 중심, 낮은 위험',
        'MODERATE':     '중립형 - 안정과 수익 균형',
        'AGGRESSIVE':   '공격형 - 높은 수익 추구',
    }
    OCCUPATION_MAP = {
        'EMPLOYEE':    '직장인 (급여소득자)',
        'SELF_EMPLOY': '자영업자 (개인사업자)',
        'STUDENT':     '학생',
        'HOUSEWIFE':   '주부',
        'FREELANCER':  '프리랜서',
        'ETC':         '기타',
    }

    lines = []

    if user.age_group:
        lines.append(f'연령대: {user.age_group}')

    if user.occupation:
        lines.append(f'직업: {OCCUPATION_MAP.get(user.occupation, user.occupation)}')

    if user.investment_type:
        lines.append(f'투자성향: {INVESTMENT_TYPE_MAP.get(user.investment_type, user.investment_type)}')

    # financial_goal은 JSONField(리스트) - 여러 목표를 자연어로 나열
    if user.financial_goal:
        GOAL_MAP = {
            'HOME':       '내집마련',
            'WEDDING':    '결혼자금',
            'RETIREMENT': '노후준비',
            'TRAVEL':     '여행/여가 자금',
            'EDUCATION':  '자녀교육',
            'EMERGENCY':  '비상금 마련',
            'ETC':        '기타 목표',
        }
        goals = [GOAL_MAP.get(g, g) for g in user.financial_goal]
        lines.append(f'금융목표: {", ".join(goals)}')

    if user.monthly_saving:
        lines.append(f'월 저축 가능 금액: {user.monthly_saving}만원')

    if user.investment_period:
        lines.append(f'최대 투자 기간: {user.investment_period}개월')

    return '\n'.join(lines) if lines else '금융상품 추천을 원합니다.'



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
