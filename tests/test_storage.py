from datetime import date

from triage.models import Classificacao, Ticket
from triage.storage import conectar, ids_classificados, listar, salvar

TICKET = Ticket(id=7, titulo="t", descricao="d", data_abertura=date(2026, 11, 4))
CLASS = Classificacao(categoria="rede", prioridade="alta", resumo="r", acao_sugerida="a")


def test_salva_e_lista():
    conn = conectar(":memory:")
    salvar(conn, TICKET, CLASS)
    linhas = listar(conn)
    assert len(linhas) == 1
    assert linhas[0]["categoria"] == "rede"
    assert linhas[0]["data_abertura"] == "2026-11-04"


def test_ids_classificados():
    conn = conectar(":memory:")
    assert ids_classificados(conn) == set()
    salvar(conn, TICKET, CLASS)
    assert ids_classificados(conn) == {7}


def test_salvar_de_novo_substitui_em_vez_de_duplicar():
    conn = conectar(":memory:")
    salvar(conn, TICKET, CLASS)
    nova = Classificacao(categoria="hardware", prioridade="baixa", resumo="r2", acao_sugerida="a2")
    salvar(conn, TICKET, nova)
    linhas = listar(conn)
    assert len(linhas) == 1
    assert linhas[0]["categoria"] == "hardware"


def test_cria_pasta_do_banco(tmp_path):
    conn = conectar(tmp_path / "sub" / "x.db")
    conn.close()
    assert (tmp_path / "sub" / "x.db").exists()