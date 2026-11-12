from types import SimpleNamespace

import pytest
from google.genai import errors

from triage.providers.base import ErroProvedor, LimiteExcedido
from triage.providers.gemini import MODELO_PADRAO, GeminiProvider


class _RespostaFalsa:
    def __init__(self, text):
        self.text = text


class _ModelosFalsos:
    def __init__(self, resultado):
        self._resultado = resultado
        self.ultima_chamada = None

    def generate_content(self, **kwargs):
        self.ultima_chamada = kwargs
        if isinstance(self._resultado, Exception):
            raise self._resultado
        return self._resultado


def _provedor(monkeypatch, resultado):
    p = GeminiProvider(api_key="chave-falsa")
    p._client = SimpleNamespace(models=_ModelosFalsos(resultado))
    return p


def test_sem_chave_levanta_erro_claro(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ErroProvedor, match="GEMINI_API_KEY"):
        GeminiProvider()


def test_modelo_pode_vir_do_ambiente(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "modelo-x")
    assert GeminiProvider(api_key="k").modelo == "modelo-x"
    monkeypatch.delenv("GEMINI_MODEL")
    assert GeminiProvider(api_key="k").modelo == MODELO_PADRAO


def test_devolve_o_texto_da_resposta(monkeypatch):
    p = _provedor(monkeypatch, _RespostaFalsa('{"a": 1}'))
    assert p.gerar("oi") == '{"a": 1}'
    assert p._client.models.ultima_chamada["contents"] == "oi"


def test_erro_429_vira_limite_excedido(monkeypatch):
    p = _provedor(monkeypatch, errors.APIError(429, {"error": {"message": "cota"}}))
    with pytest.raises(LimiteExcedido):
        p.gerar("oi")


def test_outro_erro_de_api_vira_erro_provedor(monkeypatch):
    p = _provedor(monkeypatch, errors.APIError(500, {"error": {"message": "falha"}}))
    with pytest.raises(ErroProvedor) as exc:
        p.gerar("oi")
    assert not isinstance(exc.value, LimiteExcedido)


def test_resposta_vazia_vira_erro(monkeypatch):
    p = _provedor(monkeypatch, _RespostaFalsa(""))
    with pytest.raises(ErroProvedor, match="vazia"):
        p.gerar("oi")