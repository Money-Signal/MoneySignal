from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginSerializer, SignupSerializer


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
    serializer_class = LoginSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """POST /api/accounts/logout/ - 로그아웃 (클라이언트 토큰 삭제 방식)"""
    # 실제 토큰 삭제는 프론트엔드(localStorage)에서 처리
    return Response({'message': '로그아웃되었습니다.'}, status=status.HTTP_200_OK)
