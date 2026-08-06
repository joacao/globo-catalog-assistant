from typing import List, Tuple, Optional
from functools import lru_cache

from openai import OpenAI  # A biblioteca oficial purinha
from langfuse.decorators import observe, langfuse_context # Os rastreadores REST

from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

from app.core.config import settings
from app.core.qdrant import get_qdrant_client, COLLECTION_NAME, EMBEDDING_MODEL
from app.schemas.query import BookReference, BookFilter

class RAGService:
    def __init__(self):
        # Cliente oficial e limpo da OpenAI
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.qdrant_client = get_qdrant_client()
        self.chat_model = "gpt-4o-mini"

    @lru_cache(maxsize=1024)
    def _generate_query_embedding_cached(self, query: str) -> Tuple[float, ...]:
        response = self.openai_client.embeddings.create(
            input=query,
            model=EMBEDDING_MODEL
        )
        return tuple(response.data[0].embedding)

    def _build_qdrant_filter(self, filters: Optional[BookFilter]) -> Optional[Filter]:
        if not filters:
            return None
        must_conditions = []
        if filters.genero:
            must_conditions.append(FieldCondition(key="generos", match=MatchValue(value=filters.genero)))
        if filters.ano_minimo:
            must_conditions.append(FieldCondition(key="ano_publicacao", range=Range(gte=filters.ano_minimo)))
        return Filter(must=must_conditions) if must_conditions else None

    def _search_similar_books(self, query_vector: List[float], top_k: int = 5, filters: Optional[BookFilter] = None) -> List[dict]:
        qdrant_filter = self._build_qdrant_filter(filters)
        response = self.qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=top_k
        )
        return [point.payload for point in response.points]

    # --- O DECORATOR MÁGICO: Transforma essa função no "Trace" principal ---
    @observe(name="fluxo_rag_editora")
    async def answer_question(self, question: str, filters: Optional[BookFilter] = None) -> Tuple[str, List[BookReference]]:
        
        query_vector = list(self._generate_query_embedding_cached(question))
        retrieved_books = self._search_similar_books(query_vector, top_k=5, filters=filters)
        
        if not retrieved_books:
            langfuse_context.flush() # Garante o envio imediato
            return "Não encontrei nenhum livro no catálogo que atenda aos critérios informados.", []

        system_prompt = "Você é o Assistente de Curadoria de Catálogo da Editora Globo. Responda com base EXCLUSIVAMENTE nas informações do catálogo fornecido."
        context_str = "\n".join([f"- Título: {b.get('titulo')}, Sinopse: {b.get('sinopse')}" for b in retrieved_books])
        user_prompt = f"CATÁLOGO RECUPERADO:\n{context_str}\n\nPERGUNTA: {question}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Isolamos a chamada do LLM para injetar a medição
        answer = self._chamar_llm(messages)

        references = [
            BookReference(
                id=str(b.get("id")),
                titulo=str(b.get("titulo")),
                autores=b.get("autores") if isinstance(b.get("autores"), list) else [b.get("autores")]
            ) for b in retrieved_books
        ]

        # Força o Langfuse a enviar tudo pro painel na mesma hora!
        langfuse_context.flush()
        
        return answer, references

    # --- ESSE DECORATOR CRIA A "GENERATION" (COBRA TOKENS E CUSTO) ---
    @observe(as_type="generation", name="openai_chat")
    def _chamar_llm(self, messages: List[dict]) -> str:
        response = self.openai_client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=0.2
        )
        
        # Envia os tokens reais pro Langfuse calcular os centavos
        langfuse_context.update_current_observation(
            model=self.chat_model,
            usage={
                "promptTokens": response.usage.prompt_tokens,
                "completionTokens": response.usage.completion_tokens,
                "totalTokens": response.usage.total_tokens
            }
        )
        
        return response.choices[0].message.content

rag_service = RAGService()