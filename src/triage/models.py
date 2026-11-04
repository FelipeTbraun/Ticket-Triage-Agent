from datetime import date
from enum import Enum

from pydantic import BaseModel


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
    id: int
    titulo: str
    descricao: str
    data_abertura: date


class Classificacao(BaseModel):
    categoria: Categoria
    prioridade: Prioridade
    resumo: str
    acao_sugerida: str