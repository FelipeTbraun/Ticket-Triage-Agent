import json
from datetime import date

import pytest

from triage.classifier import ErroClassificacao, classificar, montar_prompt
from triage.models import Prioridade, Ticket
from triage.providers.base import ErroProvedor, LimiteExcedido
from triage.providers.fake import FakeProvider

TICKET = Ticket(id=1, titulo="Sem Wi-Fi", descricao="Ninguém conecta", data_abertura=date(2026, 11, 4))

JSON_OK = json.dumps(
    {"categoria": "rede", "prioridade": "alta", "resumo": "Wi-Fi fora", "acao_sugerida": "Ver o roteador"}
)


def test_classifica_com_provedor_falso():
    c = classificar(TICKET, FakeProvider())
    assert c.categoria.value == "rede"


def test_prompt_contem_dados_do_chamado_e_valores_permitidos():
    prompt = montar_prompt(TICKET)
    assert "Sem Wi-Fi" in prompt
    assert "critica" in prompt


def test_remove_cercas_de_codigo():
    c = classificar(TICKET, FakeProvider([f"```json\n{JSON_OK}\n```"]))
    assert c.prioridade is Prioridade.ALTA


def test_tenta_de_novo_quando_formato_invalido():
    provedor = FakeProvider(["isso não é json", JSON_OK])
    c = classificar(TICKET, provedor)
    assert c.prioridade is Prioridade.ALTA
    assert provedor.chamadas == 2


def test_desiste_depois_de_duas_respostas_invalidas():
    provedor = FakeProvider(["lixo", '{"categoria": "rede"}'])
    with pytest.raises(ErroClassificacao, match="formato inválido"):
        classificar(TICKET, provedor)
    assert provedor.chamadas == 2


def test_valor_fora_da_lista_conta_como_formato_invalido():
    ruim = JSON_OK.replace("alta", "urgente")
    with pytest.raises(ErroClassificacao):
        classificar(TICKET, FakeProvider([ruim, ruim]))


def test_backoff_dobra_a_espera_em_erro_429():
    esperas = []
    provedor = FakeProvider([LimiteExcedido("429"), LimiteExcedido("429"), JSON_OK])
    c = classificar(TICKET, provedor, espera_base=5, dormir=esperas.append)
    assert c.categoria.value == "rede"
    assert esperas == [5, 10]


def test_desiste_quando_o_limite_persiste():
    provedor = FakeProvider([LimiteExcedido("429")] * 4)
    with pytest.raises(ErroClassificacao, match="limite"):
        classificar(TICKET, provedor, tentativas_limite=4, dormir=lambda s: None)


def test_erro_do_provedor_vira_erro_de_classificacao():
    with pytest.raises(ErroClassificacao, match="provedor"):
        classificar(TICKET, FakeProvider([ErroProvedor("fora do ar")]))