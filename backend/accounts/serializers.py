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
            'email':    {'error_messages': {'unique': '이미 사용 중인 이메일입니다.'}},
            'nickname': {'error_messages': {'unique': '이미 사용 중인 닉네임입니다.'}},
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


class ProfileSerializer(serializers.ModelSerializer):
    """마이페이지 회원정보 조회 시리얼라이저 (읽기 전용)"""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'nickname', 'profile_image', 'provider',
            'age_group', 'monthly_saving', 'investment_type',
            'preferred_product_type', 'financial_goal', 'target_amount', 'investment_period',
            'created_at',
        ]
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """마이페이지 회원정보 수정 시리얼라이저"""

    # 비밀번호 변경은 선택사항 (카카오 유저는 비밀번호 없음)
    password         = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'provider', 'created_at',
            'nickname', 'profile_image',
            'age_group', 'monthly_saving', 'investment_type',
            'preferred_product_type', 'financial_goal', 'target_amount', 'investment_period',
            'password', 'password_confirm',
        ]
        extra_kwargs = {
            'id':                     {'read_only': True},
            'email':                  {'read_only': True},
            'provider':               {'read_only': True},
            'created_at':             {'read_only': True},
            'nickname':               {'required': False},
            'profile_image':          {'required': False},
            'age_group':              {'required': False},
            'monthly_saving':         {'required': False},
            'investment_type':        {'required': False},
            'preferred_product_type': {'required': False},
            'financial_goal':         {'required': False},
            'target_amount':          {'required': False},
            'investment_period':      {'required': False},
        }

    def validate(self, data):
        # 비밀번호 변경 시 확인 값과 일치 여부 검증
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})
        return data

    def update(self, instance, validated_data):
        # 비밀번호는 별도로 꺼내서 해싱 처리
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


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
