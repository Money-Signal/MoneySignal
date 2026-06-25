import os
import json
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from products.services import recommend_products, search_faq

GMS_API_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"  # GMS 실제 엔드포인트로 교체
MODEL = "gpt-5"

SYSTEM_PROMPT = """
너는 한국의 돈 흐름을 알려주는 MoneySignal의 금융 도우미 '한돈이'야.
MoneySignal은 예적금 상품 비교, 환율 조회, 주변 은행 찾기, 금융 영상 제공 서비스를 운영해.

아래 3가지 주제만 답변해:
1. MoneySignal 서비스 안내
   - 제공 서비스: 예적금 상품 비교, 실시간 환율 조회, 주변 은행 찾기, 금융 영상, 금/은 시세
   - 각 서비스 경로: 상단의 예·적금 상품, 상단의 환율, 상단의 주변 은행, 상단의 금융 영상, 상단의 금·은 시세
   - 회원가입: 상단의 회원가입버튼을 누르면 가능
   - 로그인: 상단의 로그인버튼을 누르면 가능
   - 찜하기, 마이페이지 등 개인화 기능은 로그인 후 이용 가능
2. 예적금 상품 추천
   - 반드시 아래 [상품 데이터]에 있는 상품만 추천해
   - 금리, 은행명, 가입 대상을 포함해서 간결하게 안내해
3. 간단한 인사 및 자기소개
   - 이름은 한돈이야
   - 인사에는 짧게 답하고 무엇을 도와줄 수 있는지 안내해

위 3가지 외의 질문 (정치, 연예, 코딩, 날씨 등)에는
"저는 금융 관련 질문만 답변할 수 있어요 😊 예적금 상품이나 MoneySignal 서비스에 대해 물어봐 주세요!" 라고만 답해.

답변 형식 규칙:
- 상품 추천 시 아래 형식으로 답해줘:

1️⃣ 상품명 (은행명)
   💰 금리: OO개월 O.OO%
   👤 가입대상: OOO

2️⃣ 상품명 (은행명)
   💰 금리: OO개월 O.OO%
   👤 가입대상: OOO

- 서비스 안내 시 아래 형식으로 답해줘:

MoneySignal에서 제공하는 서비스를 안내해드릴게요!

📈 예·적금 상품 비교
💱 실시간 환율 조회
🗺️ 주변 은행 찾기
🎬 금융 영상
📊 금·은 시세

로그인 후에는 찜하기, 마이페이지 등 개인화 기능도 이용 가능해요!
궁금한 점 있으면 말씀해 주세요 😊

- 마무리 멘트는 한 줄로 짧게
- bullet(-) 나열 방식은 사용하지 마
- 답변은 친근하고 간결하게, 너무 길지 않게
"""


def build_context(user_message):
    """유저 메시지를 기반으로 상품/FAQ 데이터를 조회해 컨텍스트 문자열을 반환"""
    context_parts = []

    # 상품 추천 데이터
    try:
        candidates = recommend_products(query_text=user_message, top_k=5)
        if candidates:
            lines = []
            for p in candidates:
                options = p.options.all()
                rates = ", ".join(
                    f"{o.save_trm}개월 {o.intr_rate2}%"
                    for o in options if o.intr_rate2
                )
                type_label = "예금" if p.product_type == "D" else "적금"
                lines.append(
                    f"- [{type_label}] {p.fin_prdt_nm} ({p.kor_co_nm}) "
                    f"| 가입대상: {p.join_member or '제한없음'} "
                    f"| 금리: {rates or '정보없음'}"
                )
            context_parts.append("[상품 데이터]\n" + "\n".join(lines))
    except Exception as e:
        print(f"recommend_products 오류: {e}")

    # FAQ 데이터
    try:
        faqs = search_faq(query_text=user_message, top_k=3)
        if faqs:
            lines = [
                f"Q: {f['question']}\nA: {f['answer']}"
                for f in faqs
            ]
            context_parts.append("[서비스 FAQ]\n" + "\n\n".join(lines))
    except Exception as e:
        print(f"search_faq 오류: {e}")

    return "\n\n".join(context_parts)


@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_response(request):
    try:
        body = request.data
        user_message = body.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': '메시지를 입력해주세요.'}, status=400)

        # 컨텍스트 조회
        context = build_context(user_message)

        # 시스템 프롬프트 + 컨텍스트 합치기
        full_system = SYSTEM_PROMPT
        if context:
            full_system += f"\n\n{context}"

        # GMS API 호출
        gms_key = os.environ.get('GMS_KEY')
        headers = {
            "Authorization": f"Bearer {gms_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "developer", "content": full_system},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 600,
            "temperature": 0.7,
        }

        res = requests.post(GMS_API_URL, headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        data = res.json()

        answer = data['choices'][0]['message']['content'].strip()
        return JsonResponse({'answer': answer}, status=200)

    except requests.exceptions.RequestException as e:
        print(f"GMS API 호출 오류: {e}")
        return JsonResponse({'error': 'AI 서비스 연결에 실패했어요. 잠시 후 다시 시도해주세요.'}, status=502)
    except Exception as e:
        print(f"챗봇 오류: {e}")
        return JsonResponse({'error': str(e)}, status=500)