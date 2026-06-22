import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginSerializer, SignupSerializer

User = get_user_model()


@api_view(['POST'])
def signup(request):
    """POST /api/accounts/signup/ - 회원가입"""
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': '회원가입이 완료되었습니다.'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """POST /api/accounts/login/ - 로그인 (access + refresh 토큰 + 유저 정보 반환)"""
    serializer_class = LoginSerializer # simplejwt의 TokenObtainPairView를 상속하고 커스텀 Serializer만 교체.


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """POST /api/accounts/logout/ - 로그아웃 (클라이언트 토큰 삭제 방식)"""
    # 실제 토큰 삭제는 프론트엔드(localStorage)에서 처리
    return Response({'message': '로그아웃되었습니다.'}, status=status.HTTP_200_OK)


def kakao_callback(request):
    """GET /api/accounts/kakao/callback/ - 카카오 OAuth2 콜백"""
    code = request.GET.get('code')

    if not code:
        return HttpResponseRedirect(f'{settings.FRONTEND_URL}/login?error=no_code')

    # 1. 인가코드 → 카카오 액세스 토큰 교환
    token_res = requests.post(
        'https://kauth.kakao.com/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_REST_API_KEY,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'code': code,
        },
    )
    kakao_access_token = token_res.json().get('access_token')

    if not kakao_access_token:
        return HttpResponseRedirect(f'{settings.FRONTEND_URL}/login?error=token_failed')

    # 2. 카카오 액세스 토큰 → 유저 정보 조회
    user_info_res = requests.get(
        'https://kapi.kakao.com/v2/user/me',
        headers={'Authorization': f'Bearer {kakao_access_token}'},
    )
    user_info = user_info_res.json()

    kakao_id      = str(user_info.get('id'))
    kakao_account = user_info.get('kakao_account', {})
    email         = kakao_account.get('email', f'kakao_{kakao_id}@kakao.local')
    nickname      = user_info.get('properties', {}).get('nickname', f'kakao_{kakao_id}')

    # 닉네임 중복 시 숫자 붙여서 처리
    base_nickname = nickname
    counter = 1
    while User.objects.filter(nickname=nickname).exclude(provider_id=kakao_id).exists():
        nickname = f'{base_nickname}_{counter}'
        counter += 1

    # 3. 유저 생성 or 조회 (처음 로그인이면 자동 회원가입)
    user, created = User.objects.get_or_create(
        provider=User.Provider.KAKAO,
        provider_id=kakao_id,
        defaults={'email': email, 'nickname': nickname},
    )

    # 4. JWT 발급 후 프론트로 리다이렉트 (is_new: 처음 로그인한 유저 여부)
    refresh = RefreshToken.for_user(user)
    return HttpResponseRedirect(
        f'{settings.FRONTEND_URL}/oauth/callback'
        f'?access={refresh.access_token}&refresh={refresh}&is_new={str(created).lower()}'
    )
