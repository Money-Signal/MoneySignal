from rest_framework import serializers
from .models import FavoriteBank

class FavoriteBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteBank
        fields = ['id', 'kakao_id', 'place_name', 'road_address_name', 'address_name', 'phone']
        read_only_fields = ['id']