from django.db import models
from django.conf import settings

class FavoriteBank(models.Model):
    # accounts 앱의 User 모델을 동적으로 참조
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_banks')
    
    # 카카오맵 API의 고유 장소 ID (예: "18512411")
    kakao_id = models.CharField(max_length=50)
    
    # 리스트를 다시 그릴 때 필요한 데이터 저장
    place_name = models.CharField(max_length=100)
    road_address_name = models.CharField(max_length=200, blank=True, null=True)
    address_name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 동일한 유저가 같은 은행을 중복 등록하는 것 방지
        unique_together = ('user', 'kakao_id')

    def __str__(self):
        return f"[{self.user.username}] {self.place_name}"