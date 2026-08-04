from fastapi import APIRouter
from app.api.v1.endpoints import ask

api_router = APIRouter()
api_router.include_router(ask.router, tags=["RAG"])