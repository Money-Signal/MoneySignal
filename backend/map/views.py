from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import FavoriteBank
from .serializers import FavoriteBankSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated]) # 로그인한 사용자만 접근 허용
def favorite_bank_list(request):
    
    # 1. 로그인한 유저의 즐겨찾기 목록 가져오기
    if request.method == 'GET':
        favorites = FavoriteBank.objects.filter(user=request.user)
        serializer = FavoriteBankSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. 즐겨찾기 토글 (있으면 해제, 없으면 등록)
    elif request.method == 'POST':
        kakao_id = request.data.get('id')
        
        if not kakao_id:
            return Response({'error': '은행 고유 ID가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 이미 등록된 즐겨찾기인지 확인
        favorite_query = FavoriteBank.objects.filter(user=request.user, kakao_id=kakao_id)
        
        if favorite_query.exists():
            # 이미 있으면 삭제 (해제)
            favorite_query.delete()
            return Response({'message': '즐겨찾기에서 제거되었습니다.', 'is_favorite': False}, status=status.HTTP_200_OK)
        else:
            # 없으면 생성 (등록)
            FavoriteBank.objects.create(
                user=request.user,
                kakao_id=kakao_id,
                place_name=request.data.get('place_name'),
                road_address_name=request.data.get('road_address_name'),
                address_name=request.data.get('address_name'),
                phone=request.data.get('phone', '')
            )
            return Response({'message': '즐겨찾기에 등록되었습니다.', 'is_favorite': True}, status=status.HTTP_201_CREATED)