import os
import urllib.request
import json
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny # 뉴스 접근 허용용

# ========================================================
# 📈 1. 기존 금/은 차트 데이터 조회 API (유지)
# ========================================================
@api_view(['GET'])
def get_asset_prices(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    asset_type = request.GET.get('asset_type', 'gold')
    
    file_name = 'Gold_prices.xlsx' if asset_type == 'gold' else 'Silver_prices.xlsx'
    file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
    
    if not os.path.exists(file_path):
        return JsonResponse({'error': f'{file_name} 파일을 찾을 수 없습니다.'}, status=404)
        
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.rename(columns={df.columns[0]: '날짜', df.columns[1]: '가격'}, inplace=True)
        df = df.dropna(subset=['날짜', '가격'])
        
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        df = df.dropna(subset=['날짜'])
        df = df.sort_values(by='날짜')
        
        file_min_date = df['날짜'].min().strftime('%Y-%m-%d') if not df.empty else ''
        file_max_date = df['날짜'].max().strftime('%Y-%m-%d') if not df.empty else ''
        
        df['가격'] = df['가격'].astype(str).str.replace(',', '', regex=False).str.strip()
        df['가격'] = pd.to_numeric(df['가격'], errors='coerce')
        df['가격'] = df['가격'].ffill().bfill().fillna(0)
        
        if start_date and start_date.strip():
            df = df[df['날짜'] >= pd.to_datetime(start_date)]
        if end_date and end_date.strip():
            df = df[df['날짜'] <= pd.to_datetime(end_date)]
            
        labels = df['날짜'].dt.strftime('%Y-%m-%d').tolist()
        prices = df['가격'].tolist()
        
        return JsonResponse({
            'asset_type': asset_type,
            'labels': labels,
            'prices': prices,
            'min_date': file_min_date,
            'max_date': file_max_date
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': f'서버 내부 에러: {str(e)}'}, status=500)


# ========================================================
# 📰 2. [신규 추가] 실시간 금/은 자산 뉴스 조회 API
# ========================================================
@api_view(['GET'])
@permission_classes([AllowAny]) # 로그인 유무와 관계없이 자유롭게 뉴스 노출
def get_commodity_news(request):
    # 🎯 프론트에서 넘어온 asset_type(gold/silver)에 맞춰 검색어 자동 튜닝
    asset_type = request.GET.get('asset_type', 'gold')
    if asset_type == 'silver':
        query = '"은" "시세"'
    else:
        query = '"금" "시세"'
    
    # settings.py의 환경변수로부터 안전하게 키 호출
    client_id = settings.NAVER_CLIENT_ID
    client_secret = settings.NAVER_CLIENT_SECRET
    
    # 한글 검색어 인코딩 및 호출 세팅 (최신순 sort=date 대신 관련도 높은 sim 사용)
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display=6&sort=sim"
    
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    
    try:
        response = urllib.request.urlopen(req)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))
            return JsonResponse({'news': data.get('items', [])}, status=200)
        else:
            return JsonResponse({'error': f"Naver API Error Code: {rescode}"}, status=rescode)
            
    except Exception as e:
        return JsonResponse({'error': f'뉴스 로드 실패: {str(e)}'}, status=500)