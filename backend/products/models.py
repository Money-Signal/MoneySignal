"""금융상품(예금/적금) 및 관심상품 모델 정의"""

from django.db import models
from django.conf import settings


class FinancialProduct(models.Model):
    """
    금융감독원 API 기반 예금/적금 상품 정보 (FSS API baseinfo 기준)
    - fin_prdt_cd(금융상품코드)가 unique key → 중복 저장 방지
    - product_type 으로 예금(D) / 적금(S) 구분
    - rsrv_type(적립유형)은 API 스펙상 options에 있으므로 ProductOption에서 관리
    """

    PRODUCT_TYPE_CHOICES = [
        ('D', '정기예금'),
        ('S', '정기적금'),
    ]

    # 금융회사 정보
    fin_co_no = models.CharField(max_length=20, verbose_name='금융회사 코드')
    kor_co_nm = models.CharField(max_length=100, verbose_name='금융회사명')

    # 상품 기본 정보
    fin_prdt_cd = models.CharField(max_length=50, unique=True, verbose_name='금융상품코드')
    fin_prdt_nm = models.CharField(max_length=200, verbose_name='금융상품명')
    product_type = models.CharField(max_length=1, choices=PRODUCT_TYPE_CHOICES, verbose_name='상품유형')

    # 가입 조건
    join_way = models.CharField(max_length=200, blank=True, verbose_name='가입방법')      # 인터넷, 스마트폰, 영업점 등
    join_member = models.CharField(max_length=200, blank=True, verbose_name='가입대상')   # 개인, 법인 등
    join_deny = models.CharField(max_length=10, blank=True, verbose_name='가입제한')      # 1: 제한없음, 2: 서민전용, 3: 일부제한

    # 금리 및 조건 설명
    spcl_cnd = models.TextField(blank=True, verbose_name='우대조건')
    etc_note = models.TextField(blank=True, verbose_name='기타 유의사항')
    mtrt_int = models.TextField(blank=True, verbose_name='만기 후 이자율')
    max_limit = models.BigIntegerField(null=True, blank=True, verbose_name='최고한도')

    # 공시 기간
    dcls_month = models.CharField(max_length=6, blank=True, verbose_name='공시 제출월')       # YYYYMM
    dcls_strt_day = models.CharField(max_length=8, blank=True, verbose_name='공시 시작일')    # YYYYMMDD
    dcls_end_day = models.CharField(max_length=8, blank=True, null=True, verbose_name='공시 종료일')
    fin_co_subm_day = models.CharField(max_length=12, blank=True, verbose_name='금융회사 제출일')

    # 찜하기 연결 (through 모델로 created_at 포함)
    liked_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserProduct',
        related_name='liked_products',
        blank=True,
        verbose_name='찜한 사용자'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초 저장일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='마지막 갱신일')

    class Meta:  # pylint: disable=too-few-public-methods
        """DB 테이블 설정"""

        db_table = 'financial_product'
        verbose_name = '금융상품'
        verbose_name_plural = '금융상품 목록'

    def __str__(self):
        return f'[{self.get_product_type_display()}] {self.kor_co_nm} - {self.fin_prdt_nm}'  # pylint: disable=no-member


class ProductOption(models.Model):
    """
    금융상품의 저축기간별 금리 옵션
    - 하나의 상품에 여러 기간(6개월, 12개월 등) 옵션이 연결됨
    - unique_together 로 동일 조건 중복 저장 방지
    """

    RATE_TYPE_CHOICES = [
        ('S', '단리'),
        ('M', '복리'),
    ]

    product = models.ForeignKey(
        FinancialProduct,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='금융상품'
    )

    # 금리 유형
    intr_rate_type = models.CharField(max_length=1, choices=RATE_TYPE_CHOICES, verbose_name='금리유형코드')
    intr_rate_type_nm = models.CharField(max_length=20, blank=True, verbose_name='금리유형명')

    # 적금 전용 (예금 옵션은 blank)
    rsrv_type = models.CharField(max_length=1, blank=True, verbose_name='적립유형코드')
    rsrv_type_nm = models.CharField(max_length=20, blank=True, verbose_name='적립유형명')

    # 기간 및 금리
    save_trm = models.IntegerField(verbose_name='저축기간(개월)')
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='기본금리')
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='최고금리')

    class Meta:  # pylint: disable=too-few-public-methods
        """DB 테이블 설정"""

        db_table = 'product_option'
        verbose_name = '상품 금리 옵션'
        verbose_name_plural = '상품 금리 옵션 목록'
        unique_together = ('product', 'intr_rate_type', 'rsrv_type', 'save_trm')

    def __str__(self):
        return (
            f'{self.product.fin_prdt_nm} - {self.save_trm}개월 '  # pylint: disable=no-member
            f'(기본 {self.intr_rate}% / 최고 {self.intr_rate2}%)'
        )


class UserProduct(models.Model):
    """
    사용자 관심상품(찜하기) 중간 테이블
    - user + product 조합이 unique → 중복 찜하기 방지
    - created_at 으로 찜한 날짜 기록 → 최근 찜한 순 정렬 가능
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='회원'
    )
    product = models.ForeignKey(
        FinancialProduct,
        on_delete=models.CASCADE,
        db_column='product_id',
        verbose_name='상품'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')

    class Meta:  # pylint: disable=too-few-public-methods
        """DB 테이블 설정"""

        db_table = 'favorite_product'
        verbose_name = '관심상품'
        verbose_name_plural = '관심상품 목록'
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user} → {self.product.fin_prdt_nm}'  # pylint: disable=no-member
