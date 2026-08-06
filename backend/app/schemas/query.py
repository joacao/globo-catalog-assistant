from typing import List, Optional
from pydantic import BaseModel, Field

class BookFilter(BaseModel):
    genero: Optional[str] = None
    ano_minimo: Optional[int] = None

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Pergunta do usuário")
    filters: Optional[BookFilter] = None
    conversation_id: Optional[str] = Field(
        None, description="ID da conversa. Se omitido, uma nova conversa é iniciada."
    )

class BookReference(BaseModel):
    id: str
    titulo: str
    autores: List[str]

class AskResponse(BaseModel):
    answer: str
    references: List[BookReference]
    conversation_id: str