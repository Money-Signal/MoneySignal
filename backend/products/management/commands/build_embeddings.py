"""
금융상품 임베딩 생성 커맨드
사용법: python manage.py build_embeddings

동작 방식:
  1. DB에서 전체 금융상품 조회
  2. 각 상품 정보를 유저 프로필과 유사도 비교에 적합한 자연어 텍스트로 변환
  3. SSAFY GMS API (text-embedding-3-small)로 1536차원 벡터 생성
  4. ChromaDB에 벡터 + 메타데이터 저장 (기존 데이터는 전량 초기화 후 재구축)
"""
# pylint: disable=no-member

import os
import time
from openai import OpenAI
from django.core.management.base import BaseCommand
from products.models import FinancialProduct
from products.chroma_client import get_collection


# SSAFY GMS 임베딩 전용 클라이언트
gms_client = OpenAI(
    api_key=os.environ.get('GMS_KEY'),
    base_url='https://gms.ssafy.io/gmsapi/api.openai.com/v1',
)

EMBEDDING_MODEL = 'text-embedding-3-small'


class Command(BaseCommand):
    help = '금융상품 임베딩을 생성하여 ChromaDB에 저장합니다.'

    def handle(self, *args, **options):
        if not os.environ.get('GMS_KEY'):
            self.stderr.write(self.style.ERROR('GMS_KEY 환경변수가 설정되지 않았습니다.'))
            return

        collection = get_collection()

        # 기존 임베딩 전체 초기화 - 상품 데이터가 바뀔 때마다 fresh하게 재구축
        existing_count = collection.count()
        if existing_count > 0:
            self.stdout.write(f'기존 임베딩 {existing_count}건 삭제 후 재구축합니다.')
            all_ids = collection.get()['ids']
            if all_ids:
                collection.delete(ids=all_ids)

        # options까지 한 번에 가져와 N+1 쿼리 방지
        products = FinancialProduct.objects.prefetch_related('options').all()
        total = products.count()
        self.stdout.write(f'총 {total}개 상품 임베딩 시작...\n')

        success, fail = 0, 0

        for i, product in enumerate(products, 1):
            text = self._build_product_text(product)
            try:
                vector = self._get_embedding(text)
                collection.add(
                    ids=[str(product.id)],   # 나중에 DB 상세조회 시 키로 사용
                    embeddings=[vector],
                    documents=[text],         # 원본 텍스트 (디버깅/검색결과 확인용)
                    metadatas=[{
                        # 추천 시 product_type 하드 필터에 사용
                        'product_type': product.product_type,
                        'kor_co_nm':    product.kor_co_nm,
                        'fin_prdt_nm':  product.fin_prdt_nm,
                    }],
                )
                success += 1
                self.stdout.write(f'  [{i}/{total}] {product.kor_co_nm} - {product.fin_prdt_nm}')
                time.sleep(0.1)  # GMS API rate limit 방지
            except Exception as e:  # pylint: disable=broad-except
                # 개별 상품 실패는 건너뛰고 계속 진행
                fail += 1
                self.stderr.write(self.style.WARNING(f'  [{i}/{total}] 실패: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n완료! 성공: {success}건 / 실패: {fail}건'))

    def _build_product_text(self, product):
        """
        상품 정보를 임베딩용 자연어 텍스트로 변환.

        핵심 설계 원칙:
          나중에 유저 프로필("직장인, 내집마련, 안정형 20대")을 같은 방식으로 임베딩해서
          이 텍스트와 코사인 유사도를 비교할 것임.
          따라서 join_member(가입대상), spcl_cnd(우대조건) 등
          유저 특성과 겹치는 키워드가 많이 포함되도록 구성.
        """
        product_type_nm = '정기예금' if product.product_type == 'D' else '정기적금'

        # 최고금리 기준 상위 3개 옵션만 요약 (텍스트 길이 제한)
        options = product.options.order_by('-intr_rate2')[:3]
        rate_info = ', '.join(
            f'{opt.save_trm}개월 최고 {opt.intr_rate2}%'
            for opt in options if opt.intr_rate2 is not None
        ) or '-'

        lines = [
            f'유형: {product_type_nm}',
            f'가입방법: {product.join_way or "-"}',
            f'적합 고객: {product.join_member or "제한없음"}',
            f'금리정보: {rate_info}',
            f'우대조건: {product.spcl_cnd or "-"}',
        ]
        return '\n'.join(lines)

    def _get_embedding(self, text):
        """SSAFY GMS API로 텍스트 임베딩 벡터(1536차원) 반환"""
        response = gms_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
