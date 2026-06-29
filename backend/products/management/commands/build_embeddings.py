"""
금융상품 임베딩 생성 커맨드
사용법: python manage.py build_embeddings
"""
# pylint: disable=no-member

import os
import time
from openai import OpenAI
from django.core.management.base import BaseCommand
from products.models import FinancialProduct
from products.chroma_client import get_collection

openai_client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

EMBEDDING_MODEL = 'text-embedding-3-small'


class Command(BaseCommand):
    help = '금융상품 임베딩을 생성하여 ChromaDB에 저장합니다.'

    def handle(self, *args, **options):
        if not os.environ.get('OPENAI_API_KEY'):
            self.stderr.write(self.style.ERROR('OPENAI_API_KEY 환경변수가 설정되지 않았습니다.'))
            return

        collection = get_collection()

        existing_count = collection.count()
        if existing_count > 0:
            self.stdout.write(f'기존 임베딩 {existing_count}건 삭제 후 재구축합니다.')
            all_ids = collection.get()['ids']
            if all_ids:
                collection.delete(ids=all_ids)

        products = FinancialProduct.objects.prefetch_related('options').all()
        total = products.count()
        self.stdout.write(f'총 {total}개 상품 임베딩 시작...\n')

        success, fail = 0, 0

        for i, product in enumerate(products, 1):
            text = self._build_product_text(product)
            try:
                vector = self._get_embedding(text)
                collection.add(
                    ids=[str(product.id)],
                    embeddings=[vector],
                    documents=[text],
                    metadatas=[{
                        'product_type': product.product_type,
                        'kor_co_nm':    product.kor_co_nm,
                        'fin_prdt_nm':  product.fin_prdt_nm,
                    }],
                )
                success += 1
                self.stdout.write(f'  [{i}/{total}] {product.kor_co_nm} - {product.fin_prdt_nm}')
                time.sleep(0.1)
            except Exception as e:  # pylint: disable=broad-except
                fail += 1
                self.stderr.write(self.style.WARNING(f'  [{i}/{total}] 실패: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n완료! 성공: {success}건 / 실패: {fail}건'))

    def _build_product_text(self, product):
        product_type_nm = '정기예금' if product.product_type == 'D' else '정기적금'

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
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding