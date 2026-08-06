from fastapi import APIRouter, HTTPException
from app.schemas.query import AskRequest, AskResponse
from app.services.rag_service import rag_service
import traceback

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    try:
        answer, references = await rag_service.answer_question(
            question=request.question,
            filters=request.filters
        )
        return AskResponse(
            answer=answer,
            references=references
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno no processamento RAG: {str(e)}"
        )