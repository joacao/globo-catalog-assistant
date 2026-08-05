from typing import List
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings

COLLECTION_NAME = "books_catalog"
EMBEDDING_MODEL = "text-embedding-3-small"
# OpenAI text-embedding-3-small usa 1536 dimensões
VECTOR_SIZE = 1536 

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)

def init_qdrant_collection():
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Coleção '{COLLECTION_NAME}' criada com sucesso no Qdrant!")
    else:
        print(f"Coleção '{COLLECTION_NAME}' já existe.")

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    client = get_openai_client()
    
    response = client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL
    )
    
    # Extrai os vetores da resposta em batch
    return [data.embedding for data in response.data]