from typing import List, Optional
from pydantic import BaseModel, Field

class Book(BaseModel):
    id: str
    titulo: str
    autores: List[str]
    sinopse: str
    generos: List[str]
    publico_alvo: str
    ano_publicacao: int
    idioma: str
    isbn: Optional[str] = None

    def to_embedding_text(self) -> str:
        """
        Concatena os campos estratégicos para criar uma representação semântica rica.
        """

        generos_str = ", ".join(self.generos)
        autores_str = ", ".join(self.autores)
        return (
            f"Título: {self.titulo}\n"
            f"Autores: {autores_str}\n"
            f"Gêneros: {generos_str}\n"
            f"Público-alvo: {self.publico_alvo}\n"
            f"Ano de Publicação: {self.ano_publicacao}\n"
            f"Sinopse: {self.sinopse}"
        )