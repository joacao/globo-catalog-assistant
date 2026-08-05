from fastapi import APIRouter, HTTPException
from app.schemas.query import AskRequest, AskResponse
from app.services.rag_service import rag_service

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    try:
        answer, references = await rag_service.answer_question(request.question)
        return AskResponse(
            answer=answer,
            references=references
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao processar a pergunta com RAG: {str(e)}"
        )