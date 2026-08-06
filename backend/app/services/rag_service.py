import uuid
from collections import defaultdict
from typing import List, Tuple, Optional, Dict
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

        # --- Estado de conversa (multi-turn) ---
        # POC: guardado em memória do processo. Não sobrevive a restart do
        # container e não é compartilhado entre múltiplas instâncias.
        # Em produção isso viraria Redis (com TTL de sessão).
        self._conversation_history: Dict[str, List[dict]] = defaultdict(list)
        self._max_history_turns = 6  # janela: últimas N trocas (pergunta+resposta)

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

    # Calibrado empiricamente pro seu corpus - ver scripts/calibrate_threshold.py.
    # NÃO é um número universal: cosine similarity de embeddings não tem escala
    # fixa entre modelos, cada corpus tem sua própria distribuição de scores.
    MIN_RELEVANCE_SCORE = 0.35  # placeholder - troque pelo valor calibrado

    def _search_similar_books(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[BookFilter] = None,
        min_score: Optional[float] = None,
    ) -> List[dict]:
        qdrant_filter = self._build_qdrant_filter(filters)
        response = self.qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=top_k,
            score_threshold=min_score,  # Qdrant já descarta abaixo do corte nativamente
        )
        return [point.payload for point in response.points]

    @observe(name="condensa_pergunta")
    def _condense_question(self, question: str, history: List[dict]) -> str:
        """
        Reescreve a pergunta do usuário como uma pergunta autossuficiente,
        incorporando o contexto da conversa anterior. Isso é necessário porque
        o embedding da pergunta ISOLADA ("e esse primeiro?") não carrega
        sinal semântico suficiente pra busca vetorial funcionar bem -
        sem essa etapa, perguntas de acompanhamento buscam livros errados
        no Qdrant mesmo com o LLM final "lembrando" da conversa.
        """
        if not history:
            return question

        historico_str = "\n".join(
            f"{'Usuário' if m['role'] == 'user' else 'Assistente'}: {m['content']}"
            for m in history[-self._max_history_turns * 2:]
        )

        condense_prompt = (
            "Reescreva a PERGUNTA NOVA como uma pergunta completa e autossuficiente, "
            "incorporando o contexto necessário do HISTÓRICO abaixo. "
            "Não responda a pergunta, apenas reescreva-a. "
            "Se a pergunta nova já for autossuficiente, devolva-a sem alterações.\n\n"
            f"HISTÓRICO:\n{historico_str}\n\n"
            f"PERGUNTA NOVA: {question}\n\n"
            "PERGUNTA REESCRITA:"
        )

        response = self.openai_client.chat.completions.create(
            model=self.chat_model,
            messages=[{"role": "user", "content": condense_prompt}],
            temperature=0.0,  # queremos reescrita determinística, não criativa
        )
        return response.choices[0].message.content.strip()

    # --- O DECORATOR MÁGICO: Transforma essa função no "Trace" principal ---
    @observe(name="fluxo_rag_editora")
    async def answer_question(
        self,
        question: str,
        filters: Optional[BookFilter] = None,
        conversation_id: Optional[str] = None,
    ) -> Tuple[str, List[BookReference], str]:

        # Conversa nova recebe um ID novo; conversa existente reaproveita o histórico
        conversation_id = conversation_id or str(uuid.uuid4())
        history = self._conversation_history[conversation_id]

        # Passo de condensação: só a pergunta REESCRITA vira embedding/busca.
        # A pergunta ORIGINAL continua sendo o que o usuário digitou, usada
        # depois pra manter o histórico natural da conversa.
        search_question = self._condense_question(question, history)

        query_vector = list(self._generate_query_embedding_cached(search_question))
        retrieved_books = self._search_similar_books(
            query_vector, top_k=5, filters=filters, min_score=self.MIN_RELEVANCE_SCORE
        )
        
        if not retrieved_books:
            langfuse_context.flush() # Garante o envio imediato
            resposta_padrao = "Não encontrei nenhum livro no catálogo que atenda aos critérios informados."
            # Mesmo sem resultado, salvamos o turno: se o próximo turno disser
            # "e sobre outro autor?", o condensador precisa saber o que já foi perguntado.
            self._save_turn(conversation_id, question, resposta_padrao)
            return resposta_padrao, [], conversation_id

        system_prompt = "Você é o Assistente de Curadoria de Catálogo da Editora Globo. Responda com base EXCLUSIVAMENTE nas informações do catálogo fornecido."
        context_str = "\n".join([f"- Título: {b.get('titulo')}, Sinopse: {b.get('sinopse')}" for b in retrieved_books])
        user_prompt = f"CATÁLOGO RECUPERADO:\n{context_str}\n\nPERGUNTA: {question}"

        # Histórico entra aqui (não na busca) - é o que dá tom conversacional
        # à resposta final ("como te disse antes...", etc). Já vem limitado
        # pela janela de _max_history_turns definida no __init__.
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-self._max_history_turns * 2:])
        messages.append({"role": "user", "content": user_prompt})

        # Isolamos a chamada do LLM para injetar a medição
        answer = self._chamar_llm(messages)

        self._save_turn(conversation_id, question, answer)

        references = [
            BookReference(
                id=str(b.get("id")),
                titulo=str(b.get("titulo")),
                autores=b.get("autores") if isinstance(b.get("autores"), list) else [b.get("autores")]
            ) for b in retrieved_books
        ]

        # Força o Langfuse a enviar tudo pro painel na mesma hora!
        langfuse_context.flush()

        return answer, references, conversation_id

    def _save_turn(self, conversation_id: str, question: str, answer: str) -> None:
        """
        Guarda a pergunta ORIGINAL do usuário (não a reescrita) - é isso que
        deve aparecer se algum dia expormos o histórico na UI. A reescrita é
        um detalhe de implementação do retrieval, não faz parte da conversa
        do ponto de vista do usuário.
        """
        history = self._conversation_history[conversation_id]
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

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