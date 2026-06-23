from django.http import JsonResponse
from .services import get_exchange_data, get_exchange_history

def latest_rates(request):
    """전체 환율 목록 반환"""
    data = get_exchange_data()
    if not data:
        return JsonResponse({'error': '환율 데이터를 가져올 수 없습니다.'}, status=503)
    return JsonResponse(data, safe=False)

def latest_rates(request):
    data = get_exchange_data()
    if not data:
        return JsonResponse({'error': '환율 데이터를 가져올 수 없습니다.'}, status=503)
    return JsonResponse(data, safe=False)

def chart_data(request, currency_code):
    days = int(request.GET.get('days', 10))
    data = get_exchange_history(currency_code, days)
    if not data:
        return JsonResponse({'error': '데이터가 없습니다.'}, status=404)
    return JsonResponse({'chart_data': data}, safe=False)