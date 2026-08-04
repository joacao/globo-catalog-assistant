from fastapi import APIRouter, HTTPException
from app.schemas.query import AskRequest, AskResponse

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    # Stub inicial para validar o endpoint
    return AskResponse(
        answer=f"Processando sua pergunta: '{request.question}'. Integração RAG em andamento.",
        references=[]
    )