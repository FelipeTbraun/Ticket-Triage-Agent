import json

from triage.classifier import montar_prompt
from triage.models import Ticket
from triage.providers.fake import FakeProvider


def _classificar(titulo, descricao):
    t = Ticket(id=1, titulo=titulo, descricao=descricao, data_abertura="2026-11-04")
    return json.loads(FakeProvider().gerar(montar_prompt(t)))


def test_palavra_inteira_redefinir_nao_vira_rede():
    r = _classificar("Esqueci minha senha", "Preciso redefinir a senha do e-mail institucional.")
    assert r["categoria"] == "acesso"


def test_wifi_vira_rede():
    r = _classificar("Sem acesso ao Wi-Fi", "Vários usuários não conectam.")
    assert r["categoria"] == "rede"


def test_sem_palavra_conhecida_vira_outros():
    r = _classificar("Assunto qualquer", "Texto sem nada reconhecível.")
    assert r["categoria"] == "outros"