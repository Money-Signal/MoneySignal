from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """email 기반 로그인을 위한 커스텀 매니저 (기본 UserManager는 username 기반)"""

    # 일반 회원 생성
    def create_user(self, email, password=None, **extra_fields):
        # 이메일 없으면 가입 불가 
        if not email:
            raise ValueError('이메일은 필수입니다.')
        # 이메일 정규화
        email = self.normalize_email(email)
        # User 객체 생성 
        user = self.model(email=email, **extra_fields)
        # 비밀번호 암호화
        user.set_password(password)  # 평문 비밀번호 → 해시 변환
        user.save(using=self._db)
        return user

    # 관리자 생성
    def create_superuser(self, email, password=None, **extra_fields):
        # 관리자 권한 부여 
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    커스텀 유저 모델.
    AbstractUser를 상속하되 username을 제거하고 email을 로그인 식별자로 사용.
    settings.py의 AUTH_USER_MODEL = 'accounts.User' 와 함께 동작.
    """

    class AgeGroup(models.TextChoices):
        """연령대 선택지 - DB에 한글 문자열로 저장"""
        TEENS      = '10대',     '10대'
        TWENTIES   = '20대',     '20대'
        THIRTIES   = '30대',     '30대'
        FORTIES    = '40대',     '40대'
        FIFTY_PLUS = '50대 이상', '50대 이상'

    class InvestmentType(models.TextChoices):
        """투자 성향 선택지"""
        CONSERVATIVE = 'CONSERVATIVE', '안정형'
        MODERATE     = 'MODERATE',     '중립형'
        AGGRESSIVE   = 'AGGRESSIVE',   '공격형'

    class PreferredProductType(models.TextChoices):
        """선호 상품 유형 - 예금/적금/상관없음"""
        DEPOSIT = 'DEPOSIT', '예금'
        SAVING  = 'SAVING',  '적금'
        BOTH    = 'BOTH',    '상관없음'

    class Provider(models.TextChoices):
        """로그인 제공자 - 카카오 소셜 로그인 추가 시 KAKAO 분기 처리"""
        LOCAL = 'LOCAL', '일반'
        KAKAO = 'KAKAO', '카카오'

    username = None  # AbstractUser의 username 필드 제거

    # 기본 정보 (회원가입 필수)
    email         = models.EmailField(unique=True)
    nickname      = models.CharField(max_length=50, unique=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True) # 파일 업로드 시 media/profiles/ 저장

    # 금융 정보 (회원가입 선택, 마이페이지에서 수정 가능)
    age_group              = models.CharField(max_length=20, choices=AgeGroup.choices, null=True, blank=True)
    monthly_saving         = models.PositiveIntegerField(null=True, blank=True, help_text='월 저축 가능 금액, 단위: 만원')
    investment_type        = models.CharField(max_length=20, choices=InvestmentType.choices, null=True, blank=True)
    preferred_product_type = models.CharField(max_length=10, choices=PreferredProductType.choices, null=True, blank=True)
    financial_goal         = models.CharField(max_length=100, null=True, blank=True)
    target_amount          = models.PositiveIntegerField(null=True, blank=True, help_text='단위: 만원')
    investment_period      = models.PositiveIntegerField(null=True, blank=True, help_text='단위: 개월')

    # 소셜 로그인 대비 필드
    provider    = models.CharField(max_length=10, choices=Provider.choices, default=Provider.LOCAL)
    provider_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []  # createsuperuser 생성 시 추가 입력 필드 없음

    # 커스텀 매니저 연결 
    objects = UserManager() 

    def __str__(self):
        return self.email
