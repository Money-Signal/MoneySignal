"""
MoneySignal 서비스 Q&A FAQ 임베딩 생성 커맨드
사용법: python manage.py build_faq_embeddings
"""

import os
import time
from openai import OpenAI
from django.core.management.base import BaseCommand
from products.chroma_client import get_faq_collection

gms_client = OpenAI(
    api_key=os.environ.get('GMS_KEY'),
    base_url='https://gms.ssafy.io/gmsapi/api.openai.com/v1',
)
EMBEDDING_MODEL = 'text-embedding-3-small'

FAQ_DATA = [
    {
        'id': 'faq_001',
        'question': '회원가입은 어떻게 하나요?',
        'answer': '상단 메뉴의 회원가입 버튼을 클릭하거나 /signup 페이지에서 이메일, 비밀번호, 닉네임을 입력해 가입할 수 있습니다. 카카오 소셜 로그인도 지원합니다.',
        'category': '계정',
    },
    {
        'id': 'faq_002',
        'question': '로그인은 어떻게 하나요?',
        'answer': '/login 페이지에서 이메일과 비밀번호로 로그인하거나, 카카오 로그인 버튼으로 소셜 로그인을 이용할 수 있습니다.',
        'category': '계정',
    },
    {
        'id': 'faq_003',
        'question': '비밀번호를 변경하고 싶어요.',
        'answer': '마이페이지에서 정보 수정 버튼을 클릭하면 비밀번호 변경 항목이 나타납니다. 새 비밀번호를 입력하고 저장하면 됩니다. 카카오 로그인 계정은 비밀번호 변경이 불가합니다.',
        'category': '계정',
    },
    {
        'id': 'faq_004',
        'question': '회원 탈퇴는 어떻게 하나요?',
        'answer': '마이페이지 하단 서비스 메뉴에서 회원탈퇴 버튼을 클릭하면 탈퇴할 수 있습니다. 탈퇴 후에는 계정 복구가 불가합니다.',
        'category': '계정',
    },
    {
        'id': 'faq_005',
        'question': '투자 성향이나 금융 정보는 어디서 설정하나요?',
        'answer': '마이페이지에서 정보 수정 버튼을 클릭하면 연령대, 직업, 투자 성향, 선호 상품 유형, 금융 목표, 월 저축 가능 금액, 투자 기간 등 금융 정보를 입력할 수 있습니다.',
        'category': '마이페이지',
    },
    {
        'id': 'faq_006',
        'question': '프로필 사진을 바꾸고 싶어요.',
        'answer': '마이페이지에서 정보 수정 모드로 진입하면 프로필 사진 위에 카메라 아이콘이 나타납니다. 클릭해서 원하는 이미지를 업로드하면 됩니다.',
        'category': '마이페이지',
    },
    {
        'id': 'faq_007',
        'question': 'AI 맞춤 추천은 어떻게 받나요?',
        'answer': '금융상품 페이지 상단에 맞춤 추천 섹션이 있습니다. 마이페이지에서 투자 성향, 금융 목표, 직업 등 금융 정보를 입력하면 AI가 유사도 분석을 통해 최적의 상품을 추천해드립니다.',
        'category': '상품 추천',
    },
    {
        'id': 'faq_008',
        'question': '추천 상품이 바뀌지 않아요.',
        'answer': '추천 결과는 세션 동안 캐시됩니다. 마이페이지에서 금융 정보를 수정하고 저장하면 다음 금융상품 페이지 방문 시 새로운 추천 결과가 나타납니다.',
        'category': '상품 추천',
    },
    {
        'id': 'faq_009',
        'question': '예금과 적금의 차이가 뭔가요?',
        'answer': '예금은 목돈을 한 번에 맡기고 이자를 받는 상품이고, 적금은 매달 일정 금액을 납입해서 만기에 원금과 이자를 받는 상품입니다. MoneySignal에서는 두 유형 모두 비교하고 추천받을 수 있습니다.',
        'category': '금융 상품',
    },
    {
        'id': 'faq_010',
        'question': '금융상품 비교는 어떻게 하나요?',
        'answer': '상단 메뉴의 금융상품 페이지에서 예금/적금 탭을 선택하고 은행명으로 필터링해 원하는 상품을 비교할 수 있습니다. 각 상품 카드를 클릭하면 금리 옵션 상세 정보도 확인 가능합니다.',
        'category': '금융 상품',
    },
    {
        'id': 'faq_011',
        'question': '상품을 찜하려면 어떻게 하나요?',
        'answer': '금융상품 목록이나 상세 페이지에서 하트 아이콘을 클릭하면 찜 목록에 추가됩니다. 마이페이지에서 찜한 상품 목록을 모아볼 수 있습니다. 찜하기는 로그인 후 이용 가능합니다.',
        'category': '금융 상품',
    },
    {
        'id': 'faq_012',
        'question': '환율은 어디서 확인하나요?',
        'answer': '상단 메뉴의 환율 페이지에서 주요 통화의 실시간 환율을 확인할 수 있습니다. 환율 계산기와 환율 추이 차트도 제공합니다.',
        'category': '환율',
    },
    {
        'id': 'faq_013',
        'question': '환율 계산기 사용법이 궁금해요.',
        'answer': '환율 페이지에서 원화 금액을 입력하면 주요 통화로 자동 변환됩니다. 반대로 외화 금액을 입력해 원화로 환산하는 것도 가능합니다.',
        'category': '환율',
    },
    {
        'id': 'faq_014',
        'question': '주변 은행은 어떻게 찾나요?',
        'answer': '상단 메뉴의 주변 은행 페이지에서 현재 위치 기반으로 가까운 은행 지점을 지도에서 확인할 수 있습니다. 은행명으로 필터링도 가능합니다.',
        'category': '주변 은행',
    },
    {
        'id': 'faq_015',
        'question': '챗봇은 어떤 질문을 할 수 있나요?',
        'answer': '금융상품 추천 관련 질문("노후 대비 상품 추천해줘", "안전한 적금 알려줘")과 서비스 이용 방법("찜하기는 어떻게 해?", "마이페이지에서 뭘 설정하면 돼?") 등 다양한 금융 관련 질문에 답변드립니다.',
        'category': '챗봇',
    },
    {
        'id': 'faq_016',
        'question': 'MoneySignal은 어떤 서비스인가요?',
        'answer': 'MoneySignal은 AI 기반 금융상품 추천 서비스입니다. 개인 투자 성향과 금융 목표를 분석해 맞춤 예금·적금을 추천하고, 환율 정보, 주변 은행 검색, 금융 커뮤니티, AI 챗봇 등 다양한 금융 서비스를 제공합니다.',
        'category': '서비스 소개',
    },
]


class Command(BaseCommand):
    help = '서비스 Q&A FAQ를 임베딩해 ChromaDB에 저장합니다.'

    def handle(self, *args, **options):
        if not os.environ.get('GMS_KEY'):
            self.stderr.write(self.style.ERROR('GMS_KEY 환경변수가 설정되지 않았습니다.'))
            return

        collection = get_faq_collection()

        existing = collection.count()
        if existing > 0:
            self.stdout.write(f'기존 FAQ 임베딩 {existing}건 삭제 후 재구축합니다.')
            collection.delete(ids=collection.get()['ids'])

        total = len(FAQ_DATA)
        self.stdout.write(f'총 {total}개 FAQ 임베딩 시작...\n')

        success, fail = 0, 0

        for faq in FAQ_DATA:
            text = f"질문: {faq['question']}\n답변: {faq['answer']}"
            try:
                response = gms_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
                vector = response.data[0].embedding
                collection.add(
                    ids=[faq['id']],
                    embeddings=[vector],
                    documents=[text],
                    metadatas=[{
                        'question': faq['question'],
                        'answer':   faq['answer'],
                        'category': faq['category'],
                    }],
                )
                success += 1
                self.stdout.write(f"  [{faq['id']}] {faq['question']}")
                time.sleep(0.1)
            except Exception as e:  # pylint: disable=broad-except
                fail += 1
                self.stderr.write(self.style.WARNING(f"  [{faq['id']}] 실패: {e}"))

        self.stdout.write(self.style.SUCCESS(f'\n완료! 성공: {success}건 / 실패: {fail}건'))
