import json
import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.schemas.book import Book
from app.core.qdrant import (
    get_qdrant_client, 
    init_qdrant_collection, 
    generate_embeddings_batch, 
    COLLECTION_NAME
)
from qdrant_client.models import PointStruct

def load_books_json(file_path: str) -> list[Book]:
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    return [Book(**item) for item in raw_data]

def run_ingestion(file_path: str, batch_size: int = 20):
    print("🚀 Iniciando processo de ingestão em batch no Qdrant...")
    
    init_qdrant_collection()
    books = load_books_json(file_path)
    print(f"📚 {len(books)} livros carregados do arquivo {file_path}")

    qdrant_client = get_qdrant_client()
    all_points = []

    # Processamento em lotes (batch)
    for i in range(0, len(books), batch_size):
        batch_books = books[i : i + batch_size]
        batch_texts = [book.to_embedding_text() for book in batch_books]
        
        print(f"📦 Processando lote [{i + 1} a {min(i + batch_size, len(books))}] de {len(books)}...")

        try:
            vectors = generate_embeddings_batch(batch_texts)
            
            for idx, (book, vector) in enumerate(zip(batch_books, vectors)):
                point_id = i + idx + 1
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=book.model_dump()
                )
                all_points.append(point)
                
            # Pequena pausa estratégica entre lotes para respeitar a quota
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Erro no lote [{i + 1} - {i + batch_size}]: {e}")

    if all_points:
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=all_points
        )
        print(f"✅ Ingestão concluída! {len(all_points)} de {len(books)} livros indexados no Qdrant.")

if __name__ == "__main__":
    json_path = os.getenv("BOOKS_JSON_PATH", "data/books.json")
    if not os.path.exists(json_path):
        print(f"⚠️ Arquivo {json_path} não encontrado em 'backend/data/'.")
    else:
        run_ingestion(json_path)