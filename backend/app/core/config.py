import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Assistente de Curadoria do Catálogo"
    API_V1_STR: str = "/api/v1"
    
    OPENAI_API_KEY: str 
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    
    # Lista de URLs permitidas para CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        # Procura primeiro na raiz, depois no diretório local como fallback
        env_file=(BASE_DIR / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()