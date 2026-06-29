"""금융상품 추천 및 FAQ 검색 서비스 — 챗봇 등 외부 모듈에서 호출하는 순수 함수"""

import os
from openai import OpenAI
from products.chroma_client import get_collection, get_faq_collection
from products.models import FinancialProduct

_openai_client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)
EMBEDDING_MODEL = 'text-embedding-3-small'


def recommend_products(query_text: str, top_k: int = 5) -> list:
    """
    query_text를 OpenAI 임베딩으로 변환해 ChromaDB 코사인 유사도 검색 후
    FinancialProduct 객체 리스트 반환.

    사용 예:
        from products.services import recommend_products
        results = recommend_products("노후 대비 안전한 상품 추천해줘")
    """
    response = _openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query_text)
    query_vector = response.data[0].embedding

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
    )

    candidate_ids = [int(pid) for pid in results['ids'][0]]
    if not candidate_ids:
        return []

    id_order = {pid: idx for idx, pid in enumerate(candidate_ids)}
    products = list(
        FinancialProduct.objects
        .prefetch_related('options')
        .filter(id__in=candidate_ids)
    )
    return sorted(products, key=lambda p: id_order.get(p.id, 999))


def search_faq(query_text: str, top_k: int = 3) -> list:
    """
    query_text와 유사한 FAQ 항목을 ChromaDB에서 검색해 반환.

    사용 예:
        from products.services import search_faq
        results = search_faq("찜하기는 어떻게 해?")
        # [{'question': ..., 'answer': ..., 'category': ...}, ...]
    """
    response = _openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query_text)
    query_vector = response.data[0].embedding

    collection = get_faq_collection()
    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
    )

    return [
        {
            'question': meta['question'],
            'answer':   meta['answer'],
            'category': meta['category'],
        }
        for meta in results['metadatas'][0]
    ]