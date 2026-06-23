import requests
from django.conf import settings
from datetime import datetime, timedelta
from .models import ExchangeRate

BOK_CURRENCY_MAP = {
    'USD': '0000001',
    'JPY': '0000002',
    'EUR': '0000003',
    'GBP': '0000012',
    'CAD': '0000013',
    'CHF': '0000014',
    'HKD': '0000015',
    'SEK': '0000016',
    'AUD': '0000017',
    'DKK': '0000018',
    'NOK': '0000019',
    'SAR': '0000020',
    'KWD': '0000021',
    'BHD': '0000022',
    'AED': '0000023',
    'SGD': '0000024',
    'MYR': '0000025',
    'NZD': '0000026',
    'THB': '0000028',
    'IDR': '0000029',
    'TWD': '0000031',
    'PHP': '0000034',
    'VND': '0000035',
    'INR': '0000037',
    'MXN': '0000040',
    'BRL': '0000041',
    'RUB': '0000043',
    'CNY': '0000053',
}

BOK_CURRENCY_NAME = {
    'USD': '미국 달러',
    'JPY': '일본 엔(100엔)',
    'EUR': '유로',
    'GBP': '영국 파운드',
    'CAD': '캐나다 달러',
    'CHF': '스위스 프랑',
    'HKD': '홍콩 달러',
    'SEK': '스웨덴 크로나',
    'AUD': '호주 달러',
    'DKK': '덴마크 크로나',
    'NOK': '노르웨이 크로나',
    'SAR': '사우디아라비아 리얄',
    'KWD': '쿠웨이트 디나르',
    'BHD': '바레인 디나르',
    'AED': '아랍에미리트 디르함',
    'SGD': '싱가포르 달러',
    'MYR': '말레이시아 링깃',
    'NZD': '뉴질랜드 달러',
    'THB': '태국 바트',
    'IDR': '인도네시아 루피아(100루피아)',
    'TWD': '대만 달러',
    'PHP': '필리핀 페소',
    'VND': '베트남 동(100동)',
    'INR': '인도 루피',
    'MXN': '멕시코 페소',
    'BRL': '브라질 헤알',
    'RUB': '러시아 루블',
    'CNY': '중국 위안',
}


def _fetch_bok_data(bok_code, start_date, end_date):
    auth_key = settings.KOREA_EXIM_AUTH_KEY
    url = (
        f"https://ecos.bok.or.kr/api/StatisticSearch/{auth_key}"
        f"/json/kr/1/100/731Y001/D/{start_date}/{end_date}/{bok_code}"
    )
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data.get('StatisticSearch', {}).get('row', [])
    except Exception as e:
        print(f"한국은행 API 오류: {e}")
        return []


def get_exchange_data():
    auth_key = settings.KOREA_EXIM_AUTH_KEY
    today = datetime.now()
    end_date = today.strftime("%Y%m%d")
    start_date = (today - timedelta(days=7)).strftime("%Y%m%d")  # 5 → 7일로 늘려서 전일 데이터 확보

    url = (
        f"https://ecos.bok.or.kr/api/StatisticSearch/{auth_key}"
        f"/json/kr/1/500/731Y001/D/{start_date}/{end_date}"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        rows = data.get('StatisticSearch', {}).get('row', [])
        if not rows:
            return []

        # 날짜 목록 내림차순 정렬
        dates = sorted(set(row['TIME'] for row in rows), reverse=True)
        latest_date = dates[0]
        prev_date = dates[1] if len(dates) > 1 else None

        latest_rows = {r['ITEM_CODE1']: r for r in rows if r['TIME'] == latest_date}
        prev_rows = {r['ITEM_CODE1']: r for r in rows if r['TIME'] == prev_date} if prev_date else {}

        result = []
        for cur_unit, bok_code in BOK_CURRENCY_MAP.items():
            if bok_code not in latest_rows:
                continue
            try:
                rate = float(latest_rows[bok_code].get('DATA_VALUE', '0').replace(',', ''))
            except ValueError:
                continue

            # 전일 대비 계산
            change = None
            if bok_code in prev_rows:
                try:
                    prev_rate = float(prev_rows[bok_code].get('DATA_VALUE', '0').replace(',', ''))
                    change = round(rate - prev_rate, 2)
                except ValueError:
                    pass

            result.append({
                'cur_unit': cur_unit,
                'cur_nm': BOK_CURRENCY_NAME.get(cur_unit, cur_unit),
                'deal_bas_r': str(rate),
                'change': change,  # 전일 대비 (없으면 None)
            })

        return result

    except Exception as e:
        print(f"API 오류: {e}")
        return []


def get_exchange_history(currency_code, days=30):
    qs = ExchangeRate.objects.filter(
        currency_code=currency_code
    ).order_by('date')

    if qs.count() >= days // 2:
        return [{'date': str(r.date), 'rate': r.deal_bas_r} for r in qs[:days]]

    bok_code = BOK_CURRENCY_MAP.get(currency_code)
    if not bok_code:
        print(f"{currency_code} 지원하지 않는 통화코드")
        return []

    today = datetime.now()
    end_date = today.strftime("%Y%m%d")
    start_date = (today - timedelta(days=days)).strftime("%Y%m%d")

    rows = _fetch_bok_data(bok_code, start_date, end_date)
    if not rows:
        return []

    result = []
    for row in rows:
        date_str = row.get('TIME', '')
        value = row.get('DATA_VALUE', '')

        if not date_str or not value:
            continue

        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d").date()
            rate = float(value.replace(',', ''))
        except ValueError:
            continue

        ExchangeRate.objects.get_or_create(
            currency_code=currency_code,
            date=date_obj,
            defaults={
                'currency_name': BOK_CURRENCY_NAME.get(currency_code, currency_code),
                'deal_bas_r': rate
            }
        )

        result.append({'date': str(date_obj), 'rate': rate})

    result.sort(key=lambda x: x['date'])
    return result