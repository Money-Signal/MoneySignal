"""ChromaDB 클라이언트 싱글톤 - 앱 전체에서 공유"""

import os
import chromadb

# Django BASE_DIR 기준으로 chroma_db 폴더에 저장
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, 'chroma_db')

_client = None
_collection = None


def get_collection():
    """ChromaDB 컬렉션 반환 (최초 1회만 초기화)"""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name='financial_products',
            metadata={'hnsw:space': 'cosine'},  # 코사인 유사도 사용
        )
    return _collection
