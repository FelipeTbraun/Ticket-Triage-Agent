import pytest
from pydantic import ValidationError

from triage.models import Classificacao, Prioridade, Ticket


def test_ticket_converte_tipos():
    t = Ticket(id="1", titulo="x", descricao="y", data_abertura="2026-11-04")
    assert t.id == 1
    assert t.data_abertura.year == 2026


def test_ticket_rejeita_data_invalida():
    with pytest.raises(ValidationError):
        Ticket(id=1, titulo="x", descricao="y", data_abertura="04/11/2026")


def test_classificacao_aceita_valores_permitidos():
    c = Classificacao(categoria="rede", prioridade="alta", resumo="r", acao_sugerida="a")
    assert c.prioridade is Prioridade.ALTA


def test_classificacao_rejeita_prioridade_fora_da_lista():
    with pytest.raises(ValidationError):
        Classificacao(categoria="rede", prioridade="urgente", resumo="r", acao_sugerida="a")


def test_classificacao_rejeita_resumo_vazio():
    with pytest.raises(ValidationError):
        Classificacao(categoria="rede", prioridade="alta", resumo="", acao_sugerida="a")