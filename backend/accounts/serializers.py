from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    """회원가입 시리얼라이저 - 기본 정보(필수) + 금융 정보(선택) 한 번에 처리"""

    password         = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'nickname',
            # 금융 정보 (선택)
            'age_group', 'monthly_saving', 'investment_type',
            'preferred_product_type', 'financial_goal', 'target_amount', 'investment_period',
        ]
        extra_kwargs = {
            'age_group':              {'required': False},
            'monthly_saving':         {'required': False},
            'investment_type':        {'required': False},
            'preferred_product_type': {'required': False},
            'financial_goal':         {'required': False},
            'target_amount':          {'required': False},
            'investment_period':      {'required': False},
        }

    # 비밀번호 일치 여부 확인
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})
        return data

    # 검증 통과한 데이터로 실제 User를 만드는 메서드
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        # create_user를 통해 비밀번호 해싱 처리
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """
    로그인 시리얼라이저.
    simplejwt 기본 응답(access, refresh)에 유저 기본 정보를 추가로 포함.
    """

    def validate(self, attrs):
        # okenObtainPairSerializer 부모 클래스가 이메일/비밀번호 검증하고 JWT를 자동으로 만들어줌
        data = super().validate(attrs) 
        data['user'] = {
            'id':       self.user.id,
            'email':    self.user.email,
            'nickname': self.user.nickname,
        }
        return data
