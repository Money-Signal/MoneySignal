"""DB 연결 설정 파일 - ChromaDB랑 연결하고 컬렉션을 관리하는 파일이에요."""

import os
import chromadb

# Django BASE_DIR 기준으로 chroma_db 폴더에 저장
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, 'chroma_db')

_client = None
_collection = None
_faq_collection = None


def _get_client():
    global _client
    if _client is None:
        # 앱 전체에서 ChromaDB 클라이언트를 1개만 유지 (싱글톤)
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client

# 두 개의 컬렉션 관리
def get_collection():
    """금융상품 ChromaDB 컬렉션 반환 (최초 1회만 초기화)"""
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(
            name='financial_products',
            metadata={'hnsw:space': 'cosine'},
        )
    return _collection


def get_faq_collection():
    """서비스 Q&A FAQ ChromaDB 컬렉션 반환 (최초 1회만 초기화)"""
    global _faq_collection
    if _faq_collection is None:
        _faq_collection = _get_client().get_or_create_collection(
            name='service_faq',
            metadata={'hnsw:space': 'cosine'},
        )
    return _faq_collection
