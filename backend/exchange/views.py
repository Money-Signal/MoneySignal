import os
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view

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
        # 1. 엑셀 파일 로드
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # 2. 첫 번째 열(Date)과 두 번째 열(Close/Last) 이름 표준화
        df.rename(columns={df.columns[0]: '날짜', df.columns[1]: '가격'}, inplace=True)
        
        # 3. 결측치 완전히 제거
        df = df.dropna(subset=['날짜', '가격'])
        
        # 4. 날짜 데이터 형변환 및 과거순 정렬
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        df = df.dropna(subset=['날짜'])
        df = df.sort_values(by='날짜')
        
        # 5. [중요] 엑셀 원본의 전체 사용 가능 날짜 범위 미리 추출 (방어용)
        file_min_date = df['날짜'].min().strftime('%Y-%m-%d') if not df.empty else ''
        file_max_date = df['날짜'].max().strftime('%Y-%m-%d') if not df.empty else ''
        
        # 6. 가격 데이터 전처리 (콤마 문자열 제거 후 숫자로 강제 변환)
        df['가격'] = df['가격'].astype(str).str.replace(',', '', regex=False).str.strip()
        df['가격'] = pd.to_numeric(df['가격'], errors='coerce')
        
        # 변환 과정에서 빵꾸난 데이터는 앞뒤 가격으로 자연스럽게 메꾸기
        df['가격'] = df['가격'].ffill().bfill().fillna(0)
        
        # 7. 프론트엔드가 요청한 기간 필터링 적용
        if start_date and start_date.strip():
            df = df[df['날짜'] >= pd.to_datetime(start_date)]
        if end_date and end_date.strip():
            df = df[df['날짜'] <= pd.to_datetime(end_date)]
            
        # 8. 최종 결과 포맷팅
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