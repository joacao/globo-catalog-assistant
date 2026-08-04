from pydantic_settings import BaseSettings

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Assistente de Curadoria do Catálogo"
    API_V1_STR: str = "/api/v1"
    
    GEMINI_API_KEY: str = ""
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    
    # Lista de URLs permitidas para CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"

settings = Settings()