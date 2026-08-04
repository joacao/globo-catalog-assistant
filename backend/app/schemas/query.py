from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Pergunta do usuário em linguagem natural")

class BookReference(BaseModel):
    id: str
    title: str
    author: str

class AskResponse(BaseModel):
    answer: str
    references: list[BookReference]