"""금융상품 관련 Serializer"""

from rest_framework import serializers
from products.models import FinancialProduct, ProductOption, UserProduct


class ProductOptionSerializer(serializers.ModelSerializer):
    """금리 옵션 시리얼라이저 (저축기간별 기본/최고금리)"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta"""

        model = ProductOption
        fields = ['id', 'intr_rate_type', 'intr_rate_type_nm',
                  'rsrv_type', 'rsrv_type_nm',
                  'save_trm', 'intr_rate', 'intr_rate2']


class ProductListSerializer(serializers.ModelSerializer):
    """
    상품 목록용 시리얼라이저 (간략 정보)
    - 최고금리(intr_rate2) 중 최댓값만 포함 → 목록에서 빠른 비교용
    - liked: 현재 로그인 유저가 찜했는지 여부
    """

    max_intr_rate2 = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta"""

        model = FinancialProduct
        fields = ['id', 'fin_prdt_cd', 'fin_prdt_nm', 'kor_co_nm',
                  'product_type', 'join_way', 'join_member',
                  'max_intr_rate2', 'liked']

    def get_max_intr_rate2(self, obj):
        """해당 상품의 옵션 중 최고금리(intr_rate2) 최댓값 반환"""
        rates = obj.options.values_list('intr_rate2', flat=True)
        valid = [r for r in rates if r is not None]
        return max(valid) if valid else None

    def get_liked(self, obj):
        """현재 요청 유저가 이 상품을 찜했으면 True"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.liked_users.filter(pk=request.user.pk).exists()


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    상품 상세용 시리얼라이저 (전체 정보 + 금리 옵션 포함)
    """

    options = ProductOptionSerializer(many=True, read_only=True)
    liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta"""

        model = FinancialProduct
        fields = ['id', 'fin_prdt_cd', 'fin_prdt_nm', 'kor_co_nm',
                  'product_type', 'join_way', 'join_member', 'join_deny',
                  'spcl_cnd', 'etc_note', 'mtrt_int', 'max_limit',
                  'dcls_month', 'dcls_strt_day', 'dcls_end_day',
                  'options', 'liked', 'like_count']

    def get_liked(self, obj):
        """현재 요청 유저가 이 상품을 찜했으면 True"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.liked_users.filter(pk=request.user.pk).exists()

    def get_like_count(self, obj):
        """이 상품을 찜한 유저 수"""
        return obj.liked_users.count()


class UserProductSerializer(serializers.ModelSerializer):
    """찜한 상품 목록용 시리얼라이저"""

    product = ProductListSerializer(read_only=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta"""

        model = UserProduct
        fields = ['id', 'product', 'created_at']
