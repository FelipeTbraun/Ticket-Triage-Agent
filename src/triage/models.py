from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Categoria(str, Enum):
    HARDWARE = "hardware"
    REDE = "rede"
    SOFTWARE = "software"
    ACESSO = "acesso"
    IMPRESSORA = "impressora"
    SISTEMAS = "sistemas"
    OUTROS = "outros"


class Prioridade(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class Ticket(BaseModel):
    """Um chamado de suporte, como vem do CSV."""

    id: int
    titulo: str
    descricao: str
    data_abertura: date


class Classificacao(BaseModel):
    """A resposta da IA sobre um chamado."""

    categoria: Categoria
    prioridade: Prioridade
    resumo: str = Field(min_length=1)
    acao_sugerida: str = Field(min_length=1)